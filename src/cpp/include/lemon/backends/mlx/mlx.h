#pragma once

#include "lemon/backends/backend_descriptor.h"

namespace lemon {
namespace backends {
namespace mlx {

// The mlx-engine backend descriptor (plain data). Header-only `inline const` so it
// links into both the lemonade CLI and lemond without a separate source file.
inline const BackendDescriptor descriptor = {
    /*recipe*/          "mlx-engine",
    /*display_name*/    "MLX Engine",
#ifdef _WIN32
    /*binary*/          "lemon-mlx-engine.exe",
#else
    /*binary*/          "lemon-mlx-engine",
#endif
    /*config_section*/  "",
    /*default_device*/  DEVICE_GPU,
    /*slot_policy*/     SlotPolicy::Standard,
    /*selectable_backend*/ true,
    /*uses_ctx_size*/   true,
    /*dynamic_models*/  false,
    /*options*/ {
        {"mlx_backend", "--mlx-backend", "", "BACKEND",
         "MLX backend to use (metal, rocm, cpu)", "MLX Engine Options"},
        {"mlx_args", "--mlx-args", "", "ARGS",
         "Extra arguments passed to lemon-mlx-engine", "MLX Engine Options"}
    },
    /*support*/ {
        {"metal", {"macos"},
         {{"metal", {}}}, "Apple Silicon Metal GPU"},
        {"rocm", {"linux"},
         {{"amd_gpu", {"gfx1150", "gfx1151", "gfx110X", "gfx120X"}}}, "AMD ROCm GPUs (RDNA3/RDNA4)"},
        {"cpu", {"linux", "macos"},
         {{"cpu", {"x86_64", "arm64"}}}, "CPU fallback"},
    },
    /*default_labels*/ {},
    /*required_checkpoints*/ {"main"},
    /*modality*/ "Text generation",
    /*experimental*/ true,
    /*web_display_name*/ "MLX Engine (Apple Silicon)"
};

} // namespace mlx
} // namespace backends
} // namespace lemon
