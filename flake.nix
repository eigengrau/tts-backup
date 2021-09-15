{
  description = "tts-backup";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-21.05";
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, utils }:
    (utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: {
              tts-backup = final.callPackage ./nix/tts-backup.nix { };
            })
          ];
        };
      in rec {
        packages = { tts-backup = pkgs.tts-backup; };
        defaultPackage = packages.tts-backup;
      }));
}
