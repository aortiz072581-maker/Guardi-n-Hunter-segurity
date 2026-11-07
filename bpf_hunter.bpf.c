#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "GPL";

struct event {
    u32 pid;
    u32 ppid;
    char comm[16];
    char filename[256];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB Ring Buffer
} events SEC(".maps");

SEC("kprobe/sys_execve")
int BPF_KPROBE(sys_execve, const char *filename, const char *const *argv, const char *const *envp) {
    struct event *e;
    
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    u64 id = bpf_get_current_pid_tgid();
    e->pid = id >> 32;
    e->ppid = bpf_get_current_pid_tgid();
    
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_probe_read_user_str(&e->filename, sizeof(e->filename), filename);

    bpf_ringbuf_submit(e, 0);
    return 0;
}
