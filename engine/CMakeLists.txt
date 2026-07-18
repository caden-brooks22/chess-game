cmake_minimum_required(VERSION 3.10)
project(engine_project CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(engine SHARED
	src/engine.cpp
	src/board/board.cpp
	src/search/search.cpp
	src/evaluate/evaluate.cpp
)

target_include_directories(engine PRIVATE
	${CMAKE_CURRENT_SOURCE_DIR}/include
	${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Output DLL as engine.dll
set_target_properties(engine PROPERTIES OUTPUT_NAME "engine")



# To build the project, run:
# cmake --build build --config Release

