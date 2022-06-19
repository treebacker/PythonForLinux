.intel_syntax noprefix
.globl _start

_start:
    mov rax, 1
    mov rdi, 1
    lea rsi, hello[rip]
    mov rdx, 13
    syscall
    ret

hello:
    .ascii "Hello, world\n"
