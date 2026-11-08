---
name: indd-to-idml
description: Convert Adobe InDesign (.indd, .indt) files to IDML (.idml) without InDesign using storytold/indd-utils across macOS, Linux, and Windows. Automatically checks whether indd and its dependencies (git, rustup, rustc >= 1.95) are installed before building or converting, asks before fetching URLs or writing outside the working directory, and reports converter limitations and unread objects. Use when asked to convert .indd or .indt files to .idml, inspect InDesign files, or run indd-utils.
---

# Converting INDD / INDT to IDML (`indd-utils`)

Converts native Adobe InDesign documents (`.indd`) and templates (`.indt`) to
IDML packages (`.idml`) without InDesign using
[`storytold/indd-utils`](https://github.com/storytold/indd-utils).

## Scope, Fidelity, and Filesystem Rules

- **Clean-room reverse-engineered reader (no fidelity guarantee):** INDD is an
  undocumented proprietary format. Every fact `indd-utils` relies on was found
  by comparing sample INDD files with IDML exports. The output is **not**
  identical to InDesign's own IDML export; never promise complete fidelity, even
  when a conversion emits zero warnings.
- **Supported versions and known gaps:**
  - **InDesign 1.x:** Not supported (different container).
  - **InDesign 3.0–7.5:** Converts, with document preferences (3.0–7.5), object
    style text frame settings (3.0–4.0), and the page number style (3.0) omitted
    with warnings.
  - **InDesign 8.0–21.6:** Converts, except tables from InDesign 9.2 are not
    read.
  - **Unconverted across versions:** Conditional text, QR codes, flex objects,
    transparency of placed graphics, most non-gradient transparency effects
    (bevel, satin, directional/basic feather, drop shadow offsets), hyperlink
    sources spanning paragraphs or holding anchored objects, XML
    attributes/comments/PIs/DTDs, and attributes whose value does not vary
    across public samples.
- **Commands, network fetches, and writing outside the working directory:**
  - Ask the user for confirmation and show the exact commands before fetching any
    URL (`curl https://sh.rustup.rs`, `cargo install --git ...`), installing or
    updating any toolchain or system package (`rustup`, MSVC Build Tools, `apt`,
    `winget`), or installing a binary into `~/.cargo/bin`
    (`%USERPROFILE%\.cargo\bin`).
  - During conversion, only read the user's input `.indd`/`.indt` file and write
    the single requested `.idml` output file. Never overwrite an existing file
    or write to another directory without asking first.

```text
+-----------------------------------------------------------------------+
| 1. Locate `indd` binary (PATH -> ~/.cargo/bin -> scratch build)       |
+-----------------------------------+-----------------------------------+
                                    |
                     Found? --------+-------- Not Found?
                       |                          |
                       v                          v
                       |        +---------------------------------------+
                       |        | 2. Check Dependencies (OS-specific)   |
                       |        |    - Check git & rustc >= 1.95.0      |
                       |        |    - Ask user before fetching/writing |
                       |        |    - Build or install `indd`          |
                       |        +-----------------+---------------------+
                       |                          |
                       +------------+-------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 3. Convert, Audit & Report                                            |
|    - `indd info <in.indd>`                                            |
|    - `indd convert <in.indd> <out.idml>`                              |
|    - Verify ZIP/UCF package integrity (`unzip -t` / `ZipFile`)        |
|    - `indd audit <in.indd>` (report unread objects & converter limits)|
+-----------------------------------------------------------------------+
```

---

## Step 1: Check if `indd` is Already Installed

Before installing dependencies or compiling anything, check whether the `indd`
binary already exists in `PATH`, the Cargo bin directory, or the local scratch
build directory.

### macOS & Linux

Check these locations in order:

1. `which indd`
2. `$HOME/.cargo/bin/indd`
3. `$HOME/.gemini/jetski/scratch/indd-utils/target/release/indd`

```bash
ls -la "$HOME/.cargo/bin/indd" "$HOME/.gemini/jetski/scratch/indd-utils/target/release/indd"
```

### Windows (PowerShell)

Check these locations in order:

1. `Get-Command indd -ErrorAction SilentlyContinue`
2. `$env:USERPROFILE\.cargo\bin\indd.exe`
3. `$env:USERPROFILE\.gemini\jetski\scratch\indd-utils\target\release\indd.exe`

```powershell
Test-Path "$env:USERPROFILE\.cargo\bin\indd.exe", "$env:USERPROFILE\.gemini\jetski\scratch\indd-utils\target\release\indd.exe"
```

**If `indd` is found in any of the above locations, skip Step 2 and proceed
directly to Step 3.**

---

## Step 2: Check Dependencies & Install `indd-utils`

`indd-utils` requires:
- **`git`** (to fetch the repository)
- **Rust `>= 1.95.0`** (`rust-version = "1.95"` in `Cargo.toml`, required for
  `let_chains` stabilized in 1.88 and `if_let_guard` in `src/model/story.rs`
  stabilized in 1.95). The crate has zero external dependencies in `Cargo.toml`.

> [!IMPORTANT]
> **Ask the User Before Fetching, Installing, or Writing Outside the Working Directory:**
> Never fetch from a remote URL (`https://sh.rustup.rs`,
> `https://github.com/storytold/indd-utils.git`), install or update a toolchain
> (`rustup`, MSVC Build Tools) or system package (`apt`, `winget`), or write a
> binary into `~/.cargo/bin` (`%USERPROFILE%\.cargo\bin`) without confirmation.
> Show the exact commands first and ask the user for approval.

> [!IMPORTANT]
> **Compiler Shadowing Gotcha (macOS Homebrew / Linux apt):**
> System package managers (Homebrew `/opt/homebrew/bin/rustc` or Debian/Ubuntu
> `/usr/bin/rustc`) often ship an older `rustc` earlier in `PATH` than
> `~/.cargo/bin/rustc`. Always check `~/.cargo/bin/rustc --version` directly
> and pass `RUSTC="$HOME/.cargo/bin/rustc"` when invoking `~/.cargo/bin/cargo`.

### 2.1. macOS

1. **Check `git` and `rustc`:**
   ```bash
   git --version
   ```
   ```bash
   "$HOME/.cargo/bin/rustc" --version
   ```
2. **If `rustup` is missing, show the command and ask the user before running:**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   ```
3. **If `rustc` is `< 1.95.0`, show the command and ask the user before updating `stable`:**
   ```bash
   "$HOME/.cargo/bin/rustup" update stable
   ```
4. **Build or install `indd` (show the command and ask the user before fetching from GitHub or writing to `~/.cargo/bin`):**
   - If the repo is already cloned at `$HOME/.gemini/jetski/scratch/indd-utils`:
     ```bash
     env RUSTC="$HOME/.cargo/bin/rustc" "$HOME/.cargo/bin/cargo" install --path "$HOME/.gemini/jetski/scratch/indd-utils"
     ```
   - Otherwise, install directly from GitHub:
     ```bash
     env RUSTC="$HOME/.cargo/bin/rustc" "$HOME/.cargo/bin/cargo" install --git https://github.com/storytold/indd-utils.git
     ```

### 2.2. Linux

1. **Check `git`, C linker (`cc`), and `rustc`:**
   ```bash
   git --version
   ```
   ```bash
   "$HOME/.cargo/bin/rustc" --version
   ```
   *(If `git` or `cc` is missing on Debian/Ubuntu, show `sudo apt-get update` and `sudo apt-get install -y git build-essential curl` and ask the user before running.)*
2. **If `rustup` is missing, show the command and ask the user before running:**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   ```
3. **If `rustc` is `< 1.95.0`, show the command and ask the user before updating `stable`:**
   ```bash
   "$HOME/.cargo/bin/rustup" update stable
   ```
4. **Install `indd` into `~/.cargo/bin/indd` (show the command and ask the user first):**
   ```bash
   env RUSTC="$HOME/.cargo/bin/rustc" "$HOME/.cargo/bin/cargo" install --git https://github.com/storytold/indd-utils.git
   ```

### 2.3. Windows (PowerShell)

1. **Check `git` and `rustc`:**
   ```powershell
   git --version
   ```
   ```powershell
   & "$env:USERPROFILE\.cargo\bin\rustc.exe" --version
   ```
2. **If `git`, `rustup`, or MSVC Build Tools are missing, show the commands and ask the user before running:**
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
   ```powershell
   winget install --id Rustlang.Rustup -e --source winget
   ```
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   ```
3. **If `rustc` is `< 1.95.0`, show the command and ask the user before updating `stable`:**
   ```powershell
   & "$env:USERPROFILE\.cargo\bin\rustup.exe" update stable
   ```
4. **Install `indd.exe` into `%USERPROFILE%\.cargo\bin\indd.exe` (show the command and ask the user first):**
   ```powershell
   $env:RUSTC = "$env:USERPROFILE\.cargo\bin\rustc.exe"
   & "$env:USERPROFILE\.cargo\bin\cargo.exe" install --git https://github.com/storytold/indd-utils.git
   ```

---

## Step 3: Convert INDD / INDT to IDML

Once the `indd` binary path (`<INDD_BIN>`) is resolved:

1. **Inspect Document Metadata (`indd info`)**:
   Checks the InDesign version (supports 3.0 through 21.6+; 1.x uses a different container and is unsupported), endianness, database page count, and object count.
   ```bash
   <INDD_BIN> info "/path/to/input.indd"
   ```

2. **Convert to IDML (`indd convert`)**:
   ```bash
   <INDD_BIN> convert "/path/to/input.indd" "/path/to/output.idml"
   ```
   - Non-fatal conversion issues are printed to `stderr` as `warning: ...`.
   - Default output path (if not specified by the user): same directory and basename as the input file with the `.idml` extension. Ask the user before overwriting an existing `.idml` file or writing to any other directory.

---

## Step 4: Verify Archive Integrity, Audit Unread Data, and Report

1. **Verify IDML Archive Integrity**:
   IDML files are UCF (ZIP) packages containing `mimetype`, `designmap.xml`, `Spreads/`, `Stories/`, `MasterSpreads/`, and `Resources/`. Note that this checks only ZIP container integrity, not layout/formatting fidelity.
   - **macOS / Linux**:
     ```bash
     unzip -t "/path/to/output.idml"
     ```
   - **Windows (PowerShell — decompresses every entry stream to verify CRC-32 integrity)**:
     ```powershell
     Add-Type -AssemblyName System.IO.Compression.FileSystem
     $z = [IO.Compression.ZipFile]::OpenRead("C:\path\to\output.idml")
     try { foreach ($e in $z.Entries) { $s = $e.Open(); $s.CopyTo([IO.Stream]::Null); $s.Close() } } finally { $z.Dispose() }
     ```

2. **Unread Object Audit (`indd audit`)**:
   Run `indd audit` to inspect database classes, chunks, attribute IDs, and codes in the document that the converter does not read (including items that do not emit `stderr` warnings during `indd convert`):
   ```bash
   <INDD_BIN> audit "/path/to/input.indd"
   ```

3. **Report the Result Accurately**:
   - Always present the saved `.idml` file path prominently as a clickable link (`[filename.idml](file:///absolute/path/to/filename.idml)`) along with its file size.
   - State the source InDesign version reported by `indd info`, any `stderr` warnings from `indd convert`, and a summary of unread items from `indd audit`.
   - Never promise 100% layout or formatting fidelity; mention any relevant version or feature caveats from [Scope, Fidelity, and Filesystem Rules](#scope-fidelity-and-filesystem-rules).

---

## Additional `indd` Subcommands Reference

| Subcommand | Purpose |
| :--- | :--- |
| `indd convert <in.indd> <out.idml>` | Convert INDD or INDT file to an IDML package |
| `indd info <file.indd>...` | Print InDesign version, byte order, master page, and object count |
| `indd audit [--tsv] <file.indd>` | Report database objects/chunks not read by the converter |
| `indd xmp <file.indd>` | Extract the document's XMP metadata packet |
| `indd objects <file.indd>` | List each database object (UID, class, byte length, header bytes) |
| `indd uids <file.indd>` | List UID and class for every object without reading object payloads |
| `indd dump [--full] <file.indd> <uid>...` | Hex-dump specific object chunks by UID |
