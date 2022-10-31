ENV["PYTHON"] = ""
ENV["JULIA_PKG_SERVER"] = "https://us-west.pkg.julialang.org"

using Pkg

Pkg.add("PyCall")
Pkg.build("PyCall")