import os
import yaml
from pydantic import BaseModel, ValidationError
from typing import Dict, List, Optional
from rich.console import Console
from .convertor_executor import exec_convertor
import questionary
from .msh_constants import TEMPLATE_META_FILES, DEFAULT_NONE_CHOICE


console = Console()


class Parameter(BaseModel):
    name: str
    description: str
    ask: Optional[bool] = False
    required: Optional[bool] = True
    choices: Optional[List[str]] = None
    convertor: Optional[str] = None


class TemplateMeta(BaseModel):
    parameters: List[Parameter] = []


def try_load_yaml(file_path) -> Optional[TemplateMeta]:
    """
    Attempts to load a YAML file and returns its content.
    If the file does not exist or is not a valid YAML, returns None.
    """
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            meta = TemplateMeta(**data)
            return meta
    except (FileNotFoundError, yaml.YAMLError):
        return None


def try_load_template_meta(template_path) -> Optional[TemplateMeta]:
    """
    Attempts to load the template meta data from a YAML file.
    If the file does not exist or is not a valid YAML, returns None.
    """
    try:
        for meta_file in TEMPLATE_META_FILES:
            file_path = f"{template_path}/{meta_file}"
            # file exists
            if os.path.exists(file_path):
                return try_load_yaml(file_path)
        console.print(
            f"[red]Template meta file [green]({', '.join(TEMPLATE_META_FILES)})[/green] not found in path: [cyan]{template_path}[/cyan][/red]"
        )
        raise SystemExit()
    except ValidationError as e:
        errors = e.errors()
        console.print(
            f"[red]Validation error in template meta ([cyan]{file_path}[/cyan]): [/red]"
        )
        console.print(
            f"[red]Location[/red]: {'.'.join(str(x) for x in errors[0]['loc'])}"
        )
        console.print(f"[red]Error: {errors[0]['msg']}[/red]")

        raise SystemExit()


def ask_metas(template_meta: TemplateMeta) -> Dict[str, str]:
    metas = {}
    for param in template_meta.parameters:
        if param.ask:
            question = f"Please input '{param.name}' {'[Required]' if param.required else ''}: {param.description}"
            meta = ask_for_parameter(question, param.required, param.choices)
            if meta is not None and param.convertor:
                temp_metas = metas.copy()
                temp_metas[param.name] = meta
                console.print(
                    f"[blue]$[/blue] [yellow]Converting meta for '{param.name}'[/yellow]"
                )
                convertor_meta = exec_convertor(param.convertor, temp_metas)
                if convertor_meta is not None:
                    metas[param.name] = convertor_meta
            elif meta is not None:
                metas[param.name] = meta
        else:
            if param.convertor:
                console.print(
                    f"[blue]$[/blue] [yellow]Converting meta for '{param.name}'[/yellow]"
                )
                convertor_meta = exec_convertor(param.convertor, metas)
                if param.required and convertor_meta is None:
                    console.print(
                        f"[red]Render Error: Parameter '{param.name}' is required but convert to None.[/red]"
                    )
                    raise SystemExit()

                if convertor_meta is not None:
                    metas[param.name] = convertor_meta

    return metas


def ask_for_parameter(
    question: str, required: bool, choices: Optional[List[str]]
) -> str:
    if required:
        while True:
            if choices:
                answer = questionary.select(question, choices=choices).ask()
            else:
                answer = questionary.text(question, default="").ask()

            if answer is None:
                console.print("[red]Operation cancelled by user.[/red]")
                raise SystemExit()

            if answer.strip():
                return answer.strip()

            console.print(
                "[red]This parameter is required. Please provide a value.[/red]"
            )
    else:
        if choices:
            with_empty_choice = [DEFAULT_NONE_CHOICE] + choices
            answer = questionary.select(
                question, choices=with_empty_choice, default=DEFAULT_NONE_CHOICE
            ).ask()
        else:
            answer = questionary.text(question, default="").ask()

        if answer is None:
            console.print("[red]Operation cancelled by user.[/red]")
            raise SystemExit()

        return (
            answer.strip()
            if answer.strip() and answer.strip() != DEFAULT_NONE_CHOICE
            else None
        )
