# Historical image archive — superseded

This archive records the supplied images and intermediate generations, including rejected designs. They are not current requirements and are not shown as alternatives in the main README. Several contain the very regressions the user asked to remove: mixed text sizes, buttons, language names, cursors, incorrect ordering, landscape layout or unrelated people.

`manifest.json` contains the source-file IDs, deduplicated archive filenames, hashes and original file sizes. The original PNG bytes are preserved without repainting transparency or modifying the content. Some historical sources do not have a transparent background; only the newly generated canonical exports are asserted to have verified RGBA transparency.

**Delivery boundary:** historical PNGs are in the accompanying complete ZIP. Their bulk transfer to GitHub was not completed through the available connector. The manifest is not a claim that those binaries exist in this repository. The five new canonical SVG images are committed under `../mockups/` and render directly in GitHub.

To finish the binary transfer from the complete ZIP with an authenticated GitHub CLI, run `bash face2face/portrait/tools/upload-image-assets.sh`. It checks every source hash, uses an isolated worktree, opens a PR, merges it without overriding repository checks, and removes its temporary checkout. Alternatively upload `face2face/portrait/archive/originals/` and the new mockup PNGs through GitHub. No source-image content is required to run the self-contained prototype or regenerate its current mockups.
