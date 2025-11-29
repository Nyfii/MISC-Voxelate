{ pkgs ? import <nixpkgs> { } }:

let
  fakeBpy = pkgs.python3Packages.buildPythonPackage {
    pname = "fake-bpy-module-4.3";
    version = "20250130";
    src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ea/52/d6934f234cd372b5c67e2c814115af723235afcc32ecda2804aec852ece5/fake_bpy_module_4.3-20250130-py3-none-any.whl";
        sha256 = "sha256-/VUJPe+FcCuzJLZ6hqQ7cFyHicWWXD6q3E2MtI+UN+o=";
    };
    format = "wheel";
  };

in pkgs.mkShell {
  buildInputs = [ pkgs.python313 pkgs.python313Packages.black fakeBpy ];
}

