# your python location
ENV["PYTHON"] =
ENV["JULIA_PKG_SERVER"] = "https://us-west.pkg.julialang.org"

using Pkg

Pkg.add("PyCall")
Pkg.build("PyCall")

Pkg.add(url="https://github.com/Chemical118/ProRF.jl")