import os
from pathlib import Path
from typing import List
from rich.console import Console
import questionary
import time
from .render import render_template
from .load_meta import try_load_template_meta, ask_metas
from .msh_constants import (
    DEFAULT_TEMPLATES_PATH,
    DEFAULT_OUTPUT_PATH,
    OUTPUT_TIMESTAMP_FORMAT,
)

console = Console()


def get_output_path(template_name) -> str:
    timestamp = time.strftime(OUTPUT_TIMESTAMP_FORMAT, time.localtime())
    return f"{DEFAULT_OUTPUT_PATH}/{template_name}_{timestamp}"


def list_dirs(directory: str) -> List[str]:
    """List all dirs in the given directory."""
    try:
        return [
            f
            for f in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, f))
        ]
    except FileNotFoundError:
        console.print(f"[red]Directory '{directory}' not found.[/red]")
        raise SystemExit()


def choose_template() -> dict:
    templates = list_dirs(DEFAULT_TEMPLATES_PATH)
    if len(templates) == 1:
        console.print(
            f"Only one template found: [magenta]{templates[0]}[/magenta]. Using it by default."
        )
        return {
            "name": templates[0],
            "path": f"{DEFAULT_TEMPLATES_PATH}/{templates[0]}",
        }
    choose_template = questionary.select(
        "Which one template do you want to use?",
        choices=templates,
    ).ask()

    if choose_template is None:
        console.print("[red]Operation cancelled by user.[/red]")
        raise SystemExit()

    console.print(f"You have chosen template: [magenta]{choose_template}[/magenta].")
    return {
        "name": choose_template,
        "path": f"{DEFAULT_TEMPLATES_PATH}/{choose_template}",
    }


def main():
    console.print("[cyan]1. Choose template:[/cyan]")
    template_info = choose_template()
    template_meta = try_load_template_meta(template_info["path"])
    console.print("\n[cyan]2. Ask metas for template:[/cyan]")
    metas = ask_metas(template_meta)
    output_path = get_output_path(template_info["name"])
    Path(output_path).mkdir(parents=True, exist_ok=True)
    console.print(
        f"\n[cyan]3. Rendering template to path: [magenta]{output_path}[/magenta][/cyan]"
    )
    render_template(
        template_path=template_info["path"],
        output_path=output_path,
        metas=metas,
    )
    console.print(
        f"\n[green]√：Template rendered successfully to: [magenta]{output_path}[/magenta][/green]"
    )


if __name__ == "__main__":
    main()
