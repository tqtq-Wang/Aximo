#include <stddef.h>
#include <stdlib.h>
#include <string.h>

/*
 * Minimal runtime stub for the current LLVM backend path.
 * Strings are treated as null-terminated UTF-8 byte sequences behind ptr.
 */
char *ax_runtime_string_concat(const char *left, const char *right) {
    if (left == NULL || right == NULL) {
        return NULL;
    }

    size_t left_length = strlen(left);
    size_t right_length = strlen(right);
    size_t total_length = left_length + right_length + 1;

    char *result = (char *)malloc(total_length);
    if (result == NULL) {
        return NULL;
    }

    memcpy(result, left, left_length);
    memcpy(result + left_length, right, right_length);
    result[total_length - 1] = '\0';
    return result;
}
