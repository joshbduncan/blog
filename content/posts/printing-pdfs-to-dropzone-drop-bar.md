---
title: Printing PDFs to the Dropzone Drop Bar
date: 2025-09-10
description: Skip all of the clicking-and-dragging by printing directly to the Dropzone Drop Bar right from the macOS print dialog window.
author: Josh Duncan
category: development
tags: automator, dropzone, productivity, mac, macos
---

I often use macOS’s “Print to PDF” option and have Automator Print Plugins for tasks like saving receipts, statements, and order confirmations. The problem comes when I do not know where to file a PDF right away. In the past, I would drop it on the Desktop 😱, send it to Downloads, or leave it open in Preview until I had time to deal with it. None of these options are great, so I started looking for a better way.

## An Aha Moment

That changed when I spotted a new Command Line Integration (CLI) in the release notes for Dropzone. Suddenly it clicked...

> What if I could print directly to the Drop Bar in Dropzone?

## macOS Print Plugins

On macOS, Automator Print Plugins let you do more with the PDF button in the Print dialog. Instead of just saving a file, you can set up quick actions like automatically naming, moving, or filing PDFs—right when you print. It’s a handy way to speed up routine tasks.

![macOs Print Dialog PDF Menu](/static/images/macos-print-dialog-pdf-menu.png){: loading="lazy" }

## Setting Up a Print Plugin

Upon launching Automator, [choose the "Print Plugin" workflow](https://support.apple.com/guide/automator/create-a-workflow-aut7cac58839/mac).

![Automator Startup Screen](/static/images/automator-startup-screen-print-plugin.png){: loading="lazy" }

Since we will be using the Dropzone CLI via the `dz` command, you'll only need the [`Run Shell Script`](https://support.apple.com/guide/automator/use-a-shell-script-action-in-a-workflow-autbbd4cc11c/2.10/mac/15.0) action for this workflow.

![Automator Print Plugin Workflow](/static/images/automator-print-plugin-workflow.png){: loading="lazy" }

## Code Explanation

The shell code is pretty simple, but here is a breakdown of the steps.

```bash
# 1. Set the directory (`base_dir`) for saving the PDF file.
base_dir="$HOME/Downloads/"
# 2. Move the PDF to the `base_dir`.
mv "$1" "$base_dir"
# 3. Set the final path of the PDF file.
file_path="$base_dir/$(basename "$1")"
# 4. Send the PDF file to Dropzone Drop Bar via the `dz add` command.
/usr/local/bin/dz add "$file_path"
```

### A Few Notes

1. So, how do you get your new Automator Print Plugin to show up in the Print dialog’s PDF menu? When you save the workflow in Automator as a Print Plugin, it will appear automatically in the PDF dropdown the next time you open the Print dialog. For reference, all of your custom items from that menu are stored in your user’s Library folder at `~/Library/PDF Services/`.

2. Full path to dz – Automator doesn’t always use your shell’s PATH, so call /usr/local/bin/dz explicitly.

3. By default, macOS prints PDFs to a temp directory. If you don’t need to move the file, you can send it straight to Dropzone with:

```bash
/usr/local/bin/dz add "$1"
```

## Extra Credit

You can trigger Dropzone actions too 🙌!

```bash
/usr/local/bin/dz run "File Receipt" dragged "$1"
```

## Final Thoughts

With this setup, I no longer clutter my Desktop or Downloads with stray PDFs and everything goes right into Dropzone, ready to be filed where it belongs.

🤖 Happy PDF filing!