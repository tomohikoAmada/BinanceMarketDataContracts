cmake_minimum_required(VERSION 3.24)
project(projection_core_like LANGUAGES CXX)

add_library(projection_core_like STATIC core.cpp)
target_compile_features(projection_core_like PUBLIC cxx_std_20)
