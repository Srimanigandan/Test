#include "config.h"
#include "version.h"
#include <stdio.h>
#include <stdlib.h>

// Automotive specific includes
#ifdef AUTOMOTIVE_BUILD
    #include <unistd.h>
    #include <signal.h>
#endif

// Function prototypes
int initialize_automotive_system(void);
int run_main_loop(void);
void cleanup_system(void);
void signal_handler(int signal);

int main(int argc, char *argv[]) {
    printf("Automotive Embedded System Starting...\n");
    printf("Version: %s\n", VERSION_STRING);
    printf("Build: %s\n", BUILD_NUMBER);
    
    #ifdef AUTOMOTIVE_BUILD
        printf("Automotive build mode enabled\n");
        printf("ISO26262 Compliance: %s\n", ISO26262_COMPLIANCE);
    #endif
    
    #if DEBUG_MODE
        printf("Debug mode enabled - Log level: %d\n", LOG_LEVEL);
    #endif
    
    // Initialize automotive system
    if (initialize_automotive_system() != 0) {
        fprintf(stderr, "Failed to initialize automotive system\n");
        return 1;
    }
    
    // Set up signal handling for graceful shutdown
    #ifdef AUTOMOTIVE_BUILD
        signal(SIGTERM, signal_handler);
        signal(SIGINT, signal_handler);
    #endif
    
    // Run main application loop
    int result = run_main_loop();
    
    // Cleanup
    cleanup_system();
    
    printf("Automotive system shutdown complete\n");
    return result;
}

int initialize_automotive_system(void) {
    printf("Initializing automotive system components...\n");
    
    // Initialize CAN bus
    #if CAN_BUS_ENABLED
        printf("Initializing CAN bus...\n");
        // Simulate CAN initialization
        if (1) { // Success simulation
            printf("CAN bus initialized successfully\n");
        } else {
            return -1;
        }
    #endif
    
    // Initialize LIN bus
    #if LIN_BUS_ENABLED
        printf("Initializing LIN bus...\n");
        // Simulate LIN initialization
        printf("LIN bus initialized successfully\n");
    #endif
    
    // Safety critical system checks
    #if SAFETY_CRITICAL_ENABLED
        printf("Performing safety critical system checks...\n");
        // Simulate safety checks
        printf("Safety checks passed\n");
    #endif
    
    return 0;
}

int run_main_loop(void) {
    printf("Starting main application loop...\n");
    
    int loop_count = 0;
    const int max_loops = 5; // For demonstration
    
    while (loop_count < max_loops) {
        #if DEBUG_MODE
            printf("Main loop iteration: %d\n", loop_count + 1);
        #endif
        
        // Simulate automotive control tasks
        printf("Processing automotive control tasks...\n");
        
        // Real-time constraint simulation
        #if REAL_TIME_CONSTRAINTS
            usleep(100000); // 100ms delay simulation
        #endif
        
        loop_count++;
    }
    
    printf("Main loop completed after %d iterations\n", loop_count);
    return 0;
}

void cleanup_system(void) {
    printf("Cleaning up automotive system...\n");
    
    #if CAN_BUS_ENABLED
        printf("Shutting down CAN bus...\n");
    #endif
    
    #if LIN_BUS_ENABLED
        printf("Shutting down LIN bus...\n");
    #endif
    
    printf("System cleanup completed\n");
}

void signal_handler(int signal) {
    printf("Received signal %d, initiating graceful shutdown...\n", signal);
    cleanup_system();
    exit(0);
}