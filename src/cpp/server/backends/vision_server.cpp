#include "lemon/backends/vision_server.h"
#include "lemon/backends/backend_utils.h"
#include "lemon/backend_manager.h"
#include "lemon/utils/process_manager.h"
#include "lemon/error_types.h"
#include <httplib.h>
#include <lemon/utils/aixlog.hpp>
#include <iostream>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

using namespace lemon::utils;

namespace lemon {
namespace backends {

VisionServer::VisionServer(const std::string& log_level, ModelManager* model_manager, BackendManager* backend_manager)
    : WrappedServer("vision-server", log_level, model_manager, backend_manager) {
}

VisionServer::~VisionServer() {
    unload();
}

void VisionServer::load(const std::string& model_name,
                        const ModelInfo& model_info,
                        const RecipeOptions& options,
                        bool do_not_upgrade) {
    LOG(INFO, "VisionServer") << "Loading vision server..." << std::endl;

    // Choose a port
    port_ = choose_port();
    if (port_ == 0) {
        throw std::runtime_error("Failed to find an available port for vision-server");
    }

    LOG(INFO, "VisionServer") << "Starting vision-server on port " << port_ << std::endl;

    // The vision server is a Python FastAPI app started via uvicorn
    // It must be installed beforehand (pip install lemonade-vision-server)
    std::string python_exe = "python3";

    std::vector<std::string> args = {
        "-m", "uvicorn",
        "lemonade_vision.server:create_app",
        "--factory",
        "--host", "127.0.0.1",
        "--port", std::to_string(port_)
    };

    // Pass data directory via environment variable
    std::vector<std::pair<std::string, std::string>> env_vars;
    const char* vision_data_dir = std::getenv("VISION_DATA_DIR");
    if (vision_data_dir && strlen(vision_data_dir) > 0) {
        env_vars.push_back({"VISION_DATA_DIR", vision_data_dir});
    }

    // Launch the subprocess
    process_handle_ = utils::ProcessManager::start_process(
        python_exe,
        args,
        "",         // working_dir (empty = current)
        is_debug(), // inherit_output
        false,
        env_vars
    );

    if (process_handle_.pid == 0) {
        throw std::runtime_error("Failed to start vision-server process");
    }

    LOG(INFO, "VisionServer") << "Process started with PID: " << process_handle_.pid << std::endl;

    // Wait for server to be ready (health check at /health)
    if (!wait_for_ready("/health", 60)) {
        unload();
        throw std::runtime_error("vision-server failed to start or become ready");
    }

    LOG(INFO, "VisionServer") << "Vision server ready on port " << port_ << std::endl;
}

void VisionServer::unload() {
    if (process_handle_.pid != 0) {
        LOG(INFO, "VisionServer") << "Stopping vision-server (PID: " << process_handle_.pid << ")" << std::endl;
        utils::ProcessManager::stop_process(process_handle_);
        port_ = 0;
        process_handle_ = {nullptr, 0};
    }
}

// ICompletionServer implementation (not supported - return errors)
json VisionServer::chat_completion(const json& request) {
    return json{
        {"error", {
            {"message", "Vision server does not support text completion. Use capture/deduce/product endpoints directly."},
            {"type", "unsupported_operation"},
            {"code", "model_not_applicable"}
        }}
    };
}

json VisionServer::completion(const json& request) {
    return json{
        {"error", {
            {"message", "Vision server does not support text completion. Use capture/deduce/product endpoints directly."},
            {"type", "unsupported_operation"},
            {"code", "model_not_applicable"}
        }}
    };
}

json VisionServer::responses(const json& request) {
    return json{
        {"error", {
            {"message", "Vision server does not support text completion. Use capture/deduce/product endpoints directly."},
            {"type", "unsupported_operation"},
            {"code", "model_not_applicable"}
        }}
    };
}

} // namespace backends
} // namespace lemon
