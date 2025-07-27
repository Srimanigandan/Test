#include "config.h"
#include <stdio.h>
#include <string.h>
#include <time.h>

// Automotive utility functions

// CAN message structure
typedef struct {
    unsigned int id;
    unsigned char data[8];
    unsigned char length;
} can_message_t;

// Function prototypes
int validate_can_message(can_message_t *msg);
int calculate_checksum(unsigned char *data, int length);
void log_automotive_event(const char *event, int severity);
int perform_diagnostic_check(void);

int validate_can_message(can_message_t *msg) {
    if (msg == NULL) {
        log_automotive_event("NULL CAN message pointer", 1);
        return -1;
    }
    
    // Check message ID range (automotive standard)
    if (msg->id > 0x7FF) {
        log_automotive_event("Invalid CAN ID - exceeds standard range", 2);
        return -1;
    }
    
    // Check data length
    if (msg->length > 8) {
        log_automotive_event("Invalid CAN data length", 2);
        return -1;
    }
    
    // Calculate and verify checksum
    int calculated_checksum = calculate_checksum(msg->data, msg->length - 1);
    if (msg->data[msg->length - 1] != calculated_checksum) {
        log_automotive_event("CAN message checksum mismatch", 2);
        return -1;
    }
    
    #if DEBUG_MODE
        printf("CAN message validated successfully - ID: 0x%X, Length: %d\n", 
               msg->id, msg->length);
    #endif
    
    return 0;
}

int calculate_checksum(unsigned char *data, int length) {
    if (data == NULL || length <= 0) {
        return 0;
    }
    
    unsigned char checksum = 0;
    for (int i = 0; i < length; i++) {
        checksum ^= data[i]; // Simple XOR checksum
    }
    
    return checksum;
}

void log_automotive_event(const char *event, int severity) {
    if (event == NULL) {
        return;
    }
    
    time_t current_time;
    time(&current_time);
    
    const char *severity_str;
    switch (severity) {
        case 1: severity_str = "ERROR"; break;
        case 2: severity_str = "WARNING"; break;
        case 3: severity_str = "INFO"; break;
        default: severity_str = "UNKNOWN"; break;
    }
    
    #if LOG_LEVEL >= severity
        printf("[%s] %s: %s\n", severity_str, ctime(&current_time), event);
    #endif
}

int perform_diagnostic_check(void) {
    printf("Performing automotive diagnostic checks...\n");
    
    int diagnostic_errors = 0;
    
    // Check 1: Memory usage
    #if DEBUG_MODE
        printf("Checking memory usage...\n");
    #endif
    
    // Simulate memory check
    int memory_usage = 75; // Percentage
    if (memory_usage > 90) {
        log_automotive_event("High memory usage detected", 2);
        diagnostic_errors++;
    }
    
    // Check 2: Communication bus status
    #if CAN_BUS_ENABLED
        printf("Checking CAN bus status...\n");
        // Simulate CAN bus check
        int can_errors = 0; // No errors for demo
        if (can_errors > 0) {
            log_automotive_event("CAN bus errors detected", 1);
            diagnostic_errors++;
        }
    #endif
    
    // Check 3: Safety critical systems
    #if SAFETY_CRITICAL_ENABLED
        printf("Checking safety critical systems...\n");
        // Simulate safety system check
        int safety_status = 1; // OK
        if (!safety_status) {
            log_automotive_event("Safety critical system failure", 1);
            diagnostic_errors++;
        }
    #endif
    
    // Check 4: Real-time performance
    #if REAL_TIME_CONSTRAINTS
        printf("Checking real-time performance...\n");
        // Simulate timing check
        int timing_violations = 0;
        if (timing_violations > 0) {
            log_automotive_event("Real-time timing violations detected", 2);
            diagnostic_errors++;
        }
    #endif
    
    if (diagnostic_errors == 0) {
        log_automotive_event("All diagnostic checks passed", 3);
        printf("Diagnostic check completed successfully\n");
        return 0;
    } else {
        char error_msg[100];
        snprintf(error_msg, sizeof(error_msg), 
                "Diagnostic check failed with %d errors", diagnostic_errors);
        log_automotive_event(error_msg, 1);
        return diagnostic_errors;
    }
}