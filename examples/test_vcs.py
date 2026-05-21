import pipmaster as pm_v

pm_v.ensure_packages(
    {
        "diffusers": {
            "vcs": "git+https://github.com/huggingface/diffusers.git",
            "condition": ">=0.35.1"
        }
    }
)