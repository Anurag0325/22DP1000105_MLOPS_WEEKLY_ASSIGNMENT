load("//devtools/python/blaze:pytype.bzl", "pytype_strict_library")
load("//third_party/bazel_rules/rules_python/python:py_test.bzl", "py_test")

pytype_strict_library(
    name = "geminicli_magic",
    srcs = ["geminicli_magic.py"],
    deps = [
        "//third_party/py/IPython:ipython-libs",
    ],
)

py_test(
    name = "geminicli_magic_test",
    srcs = ["geminicli_magic_test.py"],
    deps = [
        ":geminicli_magic",
        "//testing/pybase",
    ],
)
