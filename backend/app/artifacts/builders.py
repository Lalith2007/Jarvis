from app.artifacts.models import ConversationArtifact


class ArtifactBuilder:
    def conversation(
        self,
        user: str,
        assistant: str,
    ) -> ConversationArtifact:

        return ConversationArtifact(
            user=user,
            assistant=assistant,
        )


artifact_builder = ArtifactBuilder()
