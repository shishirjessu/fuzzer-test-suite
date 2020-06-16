#include <stdint.h>
#include <stdio.h>
#include <iostream>
#include <unordered_map>

std::unordered_map<uintptr_t, uintptr_t> pairs;
bool registered_exit = false;

void exit_func();

__attribute__((used))
__attribute__((optnone))
extern "C" void __trace(uintptr_t callee) {
	if (!registered_exit) {
		std::atexit(exit_func);
		registered_exit = true;
	}

	uintptr_t PC = (uintptr_t)__builtin_return_address(0);
	pairs[PC] = callee;
}

void exit_func() {
	for( const auto& pair : pairs ) {
		std::cout << "PC:" << std::hex << pair.first << "\n";
		std::cout << "Callee:" << std::hex << pair.second << "\n";
	}
}