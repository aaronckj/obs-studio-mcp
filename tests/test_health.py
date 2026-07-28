from obs_studio_mcp.tools.filters import summarize_health


def sample(fps=60.0, cpu=20.0, render=0, out_skipped=0, out_total=0):
    return {
        "fps": fps,
        "cpu": cpu,
        "render_skipped": render,
        "output_skipped": out_skipped,
        "output_total": out_total,
    }


def test_healthy_stream():
    samples = [sample(out_total=i * 60) for i in range(10)]
    out = summarize_health(samples)
    assert out["verdict"] == "healthy"
    assert out["avg_fps"] == 60.0


def test_network_drops_flagged():
    samples = [
        sample(out_skipped=i * 5, out_total=i * 60) for i in range(10)
    ]
    out = summarize_health(samples)
    assert "drops" in out["verdict"]
    assert out["drop_percent"] > 1.0


def test_gpu_overload_flagged():
    samples = [sample(render=i * 10, out_total=i * 60) for i in range(10)]
    out = summarize_health(samples)
    assert "GPU" in out["verdict"]


def test_cpu_pressure_flagged():
    samples = [sample(cpu=95.0, out_total=i * 60) for i in range(10)]
    out = summarize_health(samples)
    assert "CPU" in out["verdict"]


def test_empty_samples():
    assert summarize_health([])["verdict"] == "no samples"
