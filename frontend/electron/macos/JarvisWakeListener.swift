import AVFoundation
import Foundation
import Speech

// MARK: - Logging

func logWake(_ stage: String, _ reason: String = "") {
    let df = DateFormatter()
    df.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
    let ts = df.string(from: Date())
    let msg = "[WAKE] \(ts) \(stage) \(reason)".trimmingCharacters(in: .whitespaces)
    print(msg)
    fflush(stdout)
}

func emit(_ event: String, _ fields: [String: String] = [:]) {
    var payload = fields
    payload["event"] = event
    if let data = try? JSONSerialization.data(withJSONObject: payload),
       let line = String(data: data, encoding: .utf8) {
        print(line)
        fflush(stdout)
    }
}

// MARK: - WakePhraseDetector

final class WakePhraseDetector {
    enum Decision: String {
        case accepted = "accepted"
        case rejected = "rejected"
        case cooldown = "cooldown"
    }

    enum RejectionReason: String {
        case phraseNotExact = "phrase_not_exact"
        case cooldownActive = "cooldown_active"
        case speakerMuted  = "speaker_muted"
        case none          = ""
    }

    struct Result {
        let decision: Decision
        let reason: RejectionReason
        let matchedPhrase: String?
        let normalizedTranscript: String
    }

    private var lastActivation: Date = .distantPast
    private let cooldownSeconds: TimeInterval = 5.0

    // External gate: set to true while TTS/assistant audio is playing.
    var isSpeakerActive: Bool = false

    // Exact accepted forms (after normalization).
    private let acceptedPhrases: Set<String> = ["jarvis", "hey jarvis"]

    func normalize(_ text: String) -> String {
        var str = text.lowercased()
        str = str.components(separatedBy: .punctuationCharacters).joined(separator: " ")
        str = str.replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
        return str.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    func process(transcript: String, simulateTime: Date? = nil) -> Result {
        let normalized = normalize(transcript)

        // 1. Speaker gate — ignore wake if JARVIS is currently speaking.
        if isSpeakerActive {
            return Result(
                decision: .rejected,
                reason: .speakerMuted,
                matchedPhrase: nil,
                normalizedTranscript: normalized
            )
        }

        // 2. Exact equality match only — no contains/startsWith/regex.
        guard acceptedPhrases.contains(normalized) else {
            return Result(
                decision: .rejected,
                reason: .phraseNotExact,
                matchedPhrase: nil,
                normalizedTranscript: normalized
            )
        }

        // 3. Cooldown gate.
        let now = simulateTime ?? Date()
        if now.timeIntervalSince(lastActivation) < cooldownSeconds {
            return Result(
                decision: .cooldown,
                reason: .cooldownActive,
                matchedPhrase: normalized,
                normalizedTranscript: normalized
            )
        }

        lastActivation = now
        return Result(
            decision: .accepted,
            reason: .none,
            matchedPhrase: normalized,
            normalizedTranscript: normalized
        )
    }
}

// MARK: - WakeListener

final class WakeListener {
    private let audioEngine = AVAudioEngine()
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var framesSinceHeartbeat = 0
    private var heartbeatTimer: Timer?
    private let detector = WakePhraseDetector()

    // 300 ms stabilization: fires after the transcript stops growing.
    private var stabilizationTimer: Timer?
    private var lastTranscript: String = ""
    private var lastResult: SFSpeechRecognitionResult?
    private var taskGeneration: Int = 0
    private let audioLock = NSLock()

    func start() {
        logWake("Lifecycle", "listener_started")
        guard let recognizer else {
            logWake("Wake-word engine initialization", "failure: SFSpeechRecognizer unavailable")
            emit("error", ["message": "SFSpeechRecognizer unavailable"])
            exit(1)
        }

        guard recognizer.isAvailable else {
            logWake("Wake-word engine initialization", "failure: SFSpeechRecognizer not available")
            emit("error", ["message": "SFSpeechRecognizer not available"])
            exit(1)
        }
        logWake("Wake-word engine initialization", "success")

        logWake("Permission status", "Requesting speech permission")
        requestSpeechPermission { [weak self] allowed in
            guard allowed else {
                logWake("Permission status", "failure: Speech permission denied")
                emit("error", ["message": "Speech recognition permission denied"])
                exit(1)
            }
            logWake("Permission status", "Requesting microphone permission")
            self?.requestMicrophonePermission { micAllowed in
                guard micAllowed else {
                    logWake("Permission status", "failure: Microphone permission denied")
                    emit("error", ["message": "Microphone permission denied"])
                    exit(1)
                }
                logWake("Permission status", "success")
                self?.beginRecognition()
            }
        }
    }

    // Called from Electron IPC (via stdin JSON) when TTS starts/stops.
    func setSpeakerActive(_ active: Bool) {
        detector.isSpeakerActive = active
        logWake("Speaker gate", active ? "enabled (muting wake)" : "disabled (wake active)")
    }

    private func requestSpeechPermission(_ completion: @escaping (Bool) -> Void) {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                emit("speech-permission", ["status": "\(status.rawValue)"])
                completion(status == .authorized)
            }
        }
    }

    private func requestMicrophonePermission(_ completion: @escaping (Bool) -> Void) {
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            DispatchQueue.main.async {
                emit("microphone-permission", ["granted": granted ? "true" : "false"])
                completion(granted)
            }
        }
    }

    private func beginRecognition() {
        logWake("Microphone initialization", "Starting")
        task?.cancel()
        task = nil

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        if #available(macOS 13.0, *) {
            request.addsPunctuation = false
        }
        self.request = request

        let inputNode = audioEngine.inputNode
        inputNode.removeTap(onBus: 0)
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { [weak self] buffer, _ in
            guard let self = self else { return }
            self.framesSinceHeartbeat += 1
            self.audioLock.lock()
            self.request?.append(buffer)
            self.audioLock.unlock()
        }

        heartbeatTimer?.invalidate()
        heartbeatTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            guard let self else { return }
            let frames = self.framesSinceHeartbeat
            self.framesSinceHeartbeat = 0
            emit("heartbeat", [
                "engine_running": self.audioEngine.isRunning ? "true" : "false",
                "callback_alive": "true",
                "frames": "\(frames)"
            ])
        }

        audioEngine.prepare()
        do {
            try audioEngine.start()
            logWake("Lifecycle", "audio_engine_started")
        } catch {
            logWake("Audio engine", "failure: \(error.localizedDescription)")
            emit("audio-error", ["message": error.localizedDescription])
            exit(1)
        }

        taskGeneration += 1
        let currentGen = taskGeneration
        logWake("Lifecycle", "recognition_task_started (generation \(currentGen))")

        task = recognizer?.recognitionTask(with: request) { [weak self, currentGen] result, error in
            self?.handleRecognition(result: result, error: error, generation: currentGen)
        }
        logWake("Wake model loading", "success")
        emit("ready", ["engine": "SFSpeechRecognizer", "commands": "hey jarvis,jarvis"])
    }

    private func handleRecognition(result: SFSpeechRecognitionResult?, error: Error?, generation: Int) {
        guard generation == self.taskGeneration else {
            logWake("Lifecycle", "recognition_task_finished_ignored (stale generation: \(generation), active: \(self.taskGeneration))")
            return
        }

        if let result {
            let text = result.bestTranscription.formattedString
            guard !text.isEmpty else { return }

            emit("transcript", ["text": text])

            // Stabilization: reset 300ms timer on every new transcript.
            // Evaluation fires only after the transcript stops growing.
            if text != self.lastTranscript {
                self.lastTranscript = text
                self.lastResult = result
                self.stabilizationTimer?.invalidate()
                self.stabilizationTimer = Timer.scheduledTimer(withTimeInterval: 0.30, repeats: false) { [weak self] _ in
                    guard let self else { return }
                    self.evaluateTranscript(self.lastTranscript, result: self.lastResult)
                }
            }
        }

        if let error {
            // Ignore expected cancellation errors when we manually reset the task
            let nsErr = error as NSError
            if nsErr.domain == "kAFAssistantErrorDomain" && (nsErr.code == 216 || nsErr.code == 209 || nsErr.code == 203 || nsErr.code == 207) {
                logWake("Lifecycle", "recognition_task_finished_cancelled (code \(nsErr.code))")
                return // Task was cancelled programmatically or ended due to lack of speech upon intentional reset
            }
            
            logWake("Lifecycle", "recognition_task_finished_error: \(error.localizedDescription)")
            emit("recognition-error", ["message": error.localizedDescription])
            self.restartSoon()
        } else if result?.isFinal == true {
            logWake("Lifecycle", "recognition_task_finished_final")
        }
    }

    private func resetRecognitionTask() {
        logWake("Lifecycle", "recognition_task_cancelled")
        
        audioLock.lock()
        let oldRequest = request
        request = nil
        audioLock.unlock()
        
        oldRequest?.endAudio()
        task?.cancel()
        
        lastTranscript = ""
        lastResult = nil
        
        let newRequest = SFSpeechAudioBufferRecognitionRequest()
        newRequest.shouldReportPartialResults = true
        if #available(macOS 13.0, *) {
            newRequest.addsPunctuation = false
        }
        
        audioLock.lock()
        self.request = newRequest
        audioLock.unlock()
        
        self.taskGeneration += 1
        let currentGen = self.taskGeneration
        
        logWake("Lifecycle", "recognition_task_started (generation \(currentGen))")
        self.task = recognizer?.recognitionTask(with: newRequest) { [weak self, currentGen] result, error in
            self?.handleRecognition(result: result, error: error, generation: currentGen)
        }
    }

    private func evaluateTranscript(_ text: String, result: SFSpeechRecognitionResult? = nil) {
        var confidence: Float = 0.0
        if let seg = result?.bestTranscription.segments.last {
            confidence = seg.confidence
        }

        let detection = detector.process(transcript: text)

        emit("wake-confidence", [
            "confidence": String(format: "%.3f", confidence),
            "threshold": "0.000",
            "status": detection.decision.rawValue,
            "reason": detection.reason.rawValue,
            "phrase": detection.matchedPhrase ?? "",
            "normalized": detection.normalizedTranscript
        ])

        if detection.decision == .accepted {
            emitWake(detection.matchedPhrase ?? "jarvis")
        }
        
        // Always reset the recognition task after evaluating a stabilized transcript
        // so that the buffer clears and doesn't endlessly append subsequent speech.
        resetRecognitionTask()
    }

    private func emitWake(_ text: String) {
        logWake("Lifecycle", "cooldown_started")
        emit("wake", ["command": text])
    }

    private func restartSoon() {
        logWake("Lifecycle", "listener_stopped")
        stabilizationTimer?.invalidate()
        stabilizationTimer = nil
        heartbeatTimer?.invalidate()
        heartbeatTimer = nil
        
        audioEngine.stop()
        logWake("Lifecycle", "audio_engine_stopped")
        audioEngine.inputNode.removeTap(onBus: 0)
        
        logWake("Lifecycle", "recognition_task_cancelled")
        
        audioLock.lock()
        let oldRequest = request
        request = nil
        audioLock.unlock()
        
        oldRequest?.endAudio()
        task?.cancel()
        task = nil
        lastTranscript = ""

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.beginRecognition()
        }
    }
}

// MARK: - Unit Tests

func runTests() {
    print("--- Running WakePhraseDetector Tests (Sprint 11.4.1) ---")
    var failed = 0

    // 1. Accepted phrases (exact match required after normalization)
    let accepted: [(String, String)] = [
        ("Jarvis",        "jarvis"),
        ("jarvis",        "jarvis"),
        ("HEY JARVIS",    "hey jarvis"),
        ("Hey Jarvis",    "hey jarvis"),
        ("jarvis.",       "jarvis"),
        ("hey, jarvis",   "hey jarvis"),
    ]
    for (raw, exp) in accepted {
        let d = WakePhraseDetector()
        let res = d.process(transcript: raw)
        if res.decision == .accepted && res.matchedPhrase == exp {
            print("✅ PASS accepted: \(raw)")
        } else {
            print("❌ FAIL accepted: \(raw) → decision=\(res.decision.rawValue) phrase=\(res.matchedPhrase ?? "nil") normalized=\(res.normalizedTranscript)")
            failed += 1
        }
    }

    // 2. Rejected phrases (must never wake)
    let rejected = [
        "jarvis hello",
        "jarvis flame",
        "jarvis flame diamond",
        "jarvis please",
        "hello jarvis",
        "okay jarvis",
        "jarvis open browser",
        "jarvis extreme",
        "marvin",
        "jarvison",
        "travis",
        "harvest",
        "java",
        "jar",
        "jarv",
    ]
    for raw in rejected {
        let d = WakePhraseDetector()
        let res = d.process(transcript: raw)
        if res.decision == .rejected && res.reason == .phraseNotExact {
            print("✅ PASS rejected: \(raw)")
        } else {
            print("❌ FAIL rejected: \(raw) → decision=\(res.decision.rawValue) reason=\(res.reason.rawValue)")
            failed += 1
        }
    }

    // 3. Cooldown (5 seconds)
    let d2 = WakePhraseDetector()
    let t0 = Date()

    let r1 = d2.process(transcript: "Jarvis", simulateTime: t0)
    if r1.decision == .accepted { print("✅ PASS cooldown-1: first activation accepted") }
    else { print("❌ FAIL cooldown-1"); failed += 1 }

    let r2 = d2.process(transcript: "Jarvis", simulateTime: t0.addingTimeInterval(2.0))
    if r2.decision == .cooldown && r2.reason == .cooldownActive {
        print("✅ PASS cooldown-2: rejected at t+2s (cooldown active)")
    } else { print("❌ FAIL cooldown-2"); failed += 1 }

    let r3 = d2.process(transcript: "Jarvis", simulateTime: t0.addingTimeInterval(4.9))
    if r3.decision == .cooldown { print("✅ PASS cooldown-3: rejected at t+4.9s (still cooling)") }
    else { print("❌ FAIL cooldown-3"); failed += 1 }

    let r4 = d2.process(transcript: "Jarvis", simulateTime: t0.addingTimeInterval(5.1))
    if r4.decision == .accepted { print("✅ PASS cooldown-4: accepted at t+5.1s") }
    else { print("❌ FAIL cooldown-4"); failed += 1 }

    // 4. Speaker-mute gate
    let d3 = WakePhraseDetector()
    d3.isSpeakerActive = true
    let rMuted = d3.process(transcript: "jarvis")
    if rMuted.decision == .rejected && rMuted.reason == .speakerMuted {
        print("✅ PASS speaker-gate: muted while speaker active")
    } else { print("❌ FAIL speaker-gate"); failed += 1 }

    d3.isSpeakerActive = false
    let rUnmuted = d3.process(transcript: "jarvis")
    if rUnmuted.decision == .accepted { print("✅ PASS speaker-gate: accepted after speaker released") }
    else { print("❌ FAIL speaker-gate release"); failed += 1 }

    // Summary
    if failed > 0 {
        print("\nTests FAILED: \(failed)")
        exit(1)
    } else {
        print("\nAll tests passed.")
        exit(0)
    }
}

// MARK: - Entry Point

let args = CommandLine.arguments
if args.contains("--test") {
    runTests()
} else {
    let listener = WakeListener()
    listener.start()
    RunLoop.main.run()
}
