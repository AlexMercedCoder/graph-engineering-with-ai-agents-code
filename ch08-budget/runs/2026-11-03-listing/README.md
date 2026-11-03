# Skill listing cost

`/context` with no configuration and N project skills from `synth.py` (synthetic skills whose
descriptions follow Chapter 4's specific template, about 290 characters each), plus the 17
built-in skills. Both runs of every setting gave identical numbers.

| Setting | `/context` Skills | Project skills with descriptions | Listed by name only | Their tokens |
|---|---|---|---|---|
| flat-4 | 3.1k | 4 | 0 | 410 |
| flat-12 | 3.9k | 12 | 0 | 1,250 |
| flat-24 | 5.2k | 24 | 0 | 2,530 |
| flat-48 | 7.7k | 48 | 0 | 5,060 |
| flat-96 | 10k | 68 | 28 | 7,170 |
| flat-160 | 9.9k | 64 | 96 | 6,830 |
| flat4real (Chapter 4's four skills) | 2.6k | 4 | 0 | 340 |
| compressed (`../../skills-compressed/`) | 2.5k | 4 | 0 | 210 |
| grouped (`../../skills-grouped/`) | 2.8k | 2 categories | 0 | 180 |
| grouped48 (48 skills in 6 categories) | 3.1k | 6 categories | 0 | 420 |

The skills listed by name only were the last in alphabetical order. The 4-skill runs list the
project `code-review`, which replaces the built-in skill of the same name, so they show 16 built-ins.
