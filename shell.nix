{ pkgs ? import <nixpkgs> { } }:

let
    pythonPackages = pkgs.python314Packages;

    fakeBpy = pythonPackages.buildPythonPackage {
        pname = "fake-bpy-module";
        version = "5.1-20260730";

        format = "other";

        src = pkgs.fetchurl {
            url = "https://github.com/nutti/fake-bpy-module/releases/download/20260730/fake_bpy_modules_5.1-20260730.zip";
            sha256 = "25d729d11fd022c40626f5e54e1848229a3b0b8855c5fcae6c3efabbaaa2b534";
        };

        nativeBuildInputs = [
            pkgs.unzip
        ];

        propagatedBuildInputs = [
            pythonPackages.typing-extensions
        ];

        unpackPhase = ''
            unzip $src
            cd fake_bpy_modules_5.1-20260730
        '';

        installPhase = ''
            site=$out/${pkgs.python314.sitePackages}
            mkdir -p "$site"

            for stub in *-stubs; do
                cp -r "$stub" "$site/"

                module="''${stub%-stubs}"
                cp -r "$stub" "$site/$module"

                find "$site/$module" -type f -name '*.pyi' | while read -r file; do
                    mv "$file" "''${file%.pyi}.py"
                done
            done
        '';

        pythonImportsCheck = [ ];
    };

    python = pkgs.python314.withPackages (_: [
        fakeBpy
    ]);

in pkgs.mkShell {
    packages = [
        python
        pkgs.zip
    ];
}
