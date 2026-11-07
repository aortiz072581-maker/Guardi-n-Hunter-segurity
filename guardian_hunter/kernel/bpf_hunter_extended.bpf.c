#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "GPL";

struct extended_event {
    u32 pid;
    u32 event_type;
    char comm[16];
    char target[256];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

SEC("kprobe/sys_execve")
int BPF_KPROBE(trace_execve, const char *filename) {
    struct extended_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;
    e->pid = bpf_get_current_pid_tgid() >> 32;
    e->event_type = 1;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_probe_read_user_str(&e->target, sizeof(e->target), filename);
    bpf_ringbuf_submit(e, 0);
    return 0;
}
