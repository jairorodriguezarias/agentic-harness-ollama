package harness.quality_gate

default allow = false

allow {
    score_suficiente
    sin_vulnerabilidades
}

score_suficiente {
    input.score >= 80
}

sin_vulnerabilidades {
    input.approved == true
}