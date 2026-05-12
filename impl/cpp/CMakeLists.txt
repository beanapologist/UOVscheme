cmake_minimum_required(VERSION 3.14)
project(uov_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(uov_demo src/demo.cpp)
add_executable(uov_tests tests/test_correctness.cpp)

enable_testing()
add_test(NAME correctness COMMAND uov_tests)
