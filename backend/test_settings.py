from app.config.settings import settings

print("Model:", settings.MODEL)
print("Base URL:", settings.BASE_URL)
print("Vault:", settings.OBSIDIAN_VAULT)

if settings.NVIDIA_API_KEY:
    print("API Key: Loaded ✅")
else:
    print("API Key: Missing ❌")
