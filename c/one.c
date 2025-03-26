#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_STUDENTS 1000
#define MAX_NAME_LENGTH 50

// Custom data structure for student records
typedef struct {
    char name[MAX_NAME_LENGTH];
    int age;
    float* grades;
    int grade_count;
} Student;

// Global array to store student records
Student* student_database[MAX_STUDENTS];
int total_students = 0;

// Function prototypes
Student* create_student(const char* name, int age);
int add_grade(Student* student, float grade);
void print_student_details(const Student* student);
void free_student(Student* student);
void cleanup_database();

int main() {
    // Sample initialization
    Student* s1 = create_student("Alice", 20);
    add_grade(s1, 85.5);
    add_grade(s1, 90.0);
    add_grade(s1, 87.5);
    
    print_student_details(s1);

    // Cleanup resources
    cleanup_database();

    return 0;
}

Student* create_student(const char* name, int age) {
    if (strlen(name) >= MAX_NAME_LENGTH) {
        fprintf(stderr, "Error: Name exceeds maximum allowed length of %d characters.\n", MAX_NAME_LENGTH - 1);
        return NULL;
    }

    Student* new_student = malloc(sizeof(Student));
    if (new_student == NULL) {
        fprintf(stderr, "Memory allocation failed for new student.\n");
        return NULL;
    }

    // Safely copy the name with validation
    strncpy(new_student->name, name, MAX_NAME_LENGTH - 1);
    new_student->name[MAX_NAME_LENGTH - 1] = '\0'; // Ensure null termination

    new_student->age = age;
    new_student->grades = NULL;
    new_student->grade_count = 0;

    // Add to global database
    if (total_students < MAX_STUDENTS) {
        student_database[total_students++] = new_student;
    } else {
        fprintf(stderr, "Student database is full.\n");
        free(new_student);
        return NULL;
    }

    return new_student;
}

int add_grade(Student* student, float grade) {
    if (student == NULL) {
        return 0; // Invalid student pointer
    }

    // Optimize memory allocation by doubling the size when needed
    int new_capacity = (student->grade_count == 0) ? 1 : student->grade_count * 2;
    float* new_grades = realloc(student->grades, new_capacity * sizeof(float));
    if (new_grades == NULL) {
        fprintf(stderr, "Memory allocation failed for grades.\n");
        return 0;
    }

    student->grades = new_grades;
    student->grades[student->grade_count++] = grade;
    return 1;
}

void print_student_details(const Student* student) {
    if (student == NULL) {
        return;
    }

    printf("Name: %s\n", student->name);
    printf("Age: %d\n", student->age);
    printf("Grades: ");
    for (int i = 0; i < student->grade_count; i++) {
        printf("%.2f ", student->grades[i]);
    }
    printf("\n");
}

void free_student(Student* student) {
    if (student == NULL) {
        return;
    }

    // Free dynamically allocated grades array
    free(student->grades);
    student->grades = NULL;

    // Free the student structure itself
    free(student);
}

void cleanup_database() {
    for (int i = 0; i < total_students; i++) {
        free_student(student_database[i]);
        student_database[i] = NULL;
    }
    total_students = 0;
}