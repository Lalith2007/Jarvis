"""
Vision capabilities — Sprint 13 (architecture "vision.ocr", "vision.describe").
Local, no cloud: OCR via tesseract; describe returns grounded image facts
(dimensions/format) rather than hallucinated content.
"""
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory, CapabilityConfig, CapabilityContext,
    CapabilityDiagnostics, CapabilityManifest, CapabilityResult,
)
from app.security.permissions import permissions


class VisionOcrCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="vision.ocr", name="Vision OCR", version="1.0.0", author="System",
            description="Extract text from an image (local tesseract).",
            category=CapabilityCategory.VISION, permissions=["vision:read"],
            parameters={"image_path": {"type": "string"}},
        ), CapabilityConfig())

    def initialize(self, c): ...
    def validate(self, c):
        if not (c.runtime_state or {}).get("image_path"):
            raise ValueError("vision.ocr requires 'image_path'")
    def cleanup(self, c): ...
    def health_check(self):
        import shutil
        return "healthy" if shutil.which("tesseract") else "degraded"
    def estimate_cost(self, c): return 0.0
    def estimate_latency(self, c): return 400.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        img = permissions.resolve_if_allowed(rs["image_path"])
        if img is None:
            return CapabilityResult(success=False, status="failed", errors=["image path not allowed"])
        try:
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(str(img)))
            return CapabilityResult(success=True, status="completed",
                result={"text": text.strip(), "chars": len(text.strip())})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class VisionDescribeCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="vision.describe", name="Vision Describe", version="1.0.0", author="System",
            description="Return grounded image facts (dimensions/format/mode).",
            category=CapabilityCategory.VISION, permissions=["vision:read"],
            parameters={"image_path": {"type": "string"}},
        ), CapabilityConfig())

    def initialize(self, c): ...
    def validate(self, c):
        if not (c.runtime_state or {}).get("image_path"):
            raise ValueError("vision.describe requires 'image_path'")
    def cleanup(self, c): ...
    def health_check(self): return "healthy"
    def estimate_cost(self, c): return 0.0
    def estimate_latency(self, c): return 50.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        img = permissions.resolve_if_allowed(rs["image_path"])
        if img is None:
            return CapabilityResult(success=False, status="failed", errors=["image path not allowed"])
        try:
            from PIL import Image
            im = Image.open(str(img))
            return CapabilityResult(success=True, status="completed",
                result={"width": im.width, "height": im.height, "format": im.format, "mode": im.mode})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
