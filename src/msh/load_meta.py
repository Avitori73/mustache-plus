import os
from pydantic import ValidationError
import yaml
import questionary
from typing import Dict, List, Optional
from rich.console import Console

from .types import Parameter, TemplateMeta
from .inner_convertor_executor import exec_inner_convertor
from .convertor_executor import exec_convertor
from .msh_constants import TEMPLATE_META_FILES, DEFAULT_NONE_CHOICE


console = Console()


def try_load_yaml(file_path: str) -> Optional[TemplateMeta]:
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


def try_load_template_meta(template_path: str) -> Optional[TemplateMeta]:
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
    metas: Dict[str, str] = {}
    for param in template_meta.parameters:
        if param.ask:
            question = f"Please input '{param.name}' {'[Required]' if param.required else ''}: {param.description}"
            ask_meta: str = ask_for_parameter(question, param.required, param.choices)

            if ask_meta is not None and param.innerConvertor:
                ask_meta = apply_inner_convertors(param, ask_meta)

            if ask_meta is not None and param.convertor:
                temp_metas = metas.copy()
                temp_metas[param.name] = ask_meta
                ask_meta = apply_convertor(param, temp_metas)

            if ask_meta is not None:
                metas[param.name] = ask_meta
        else:
            convertor_meta = None

            if param.innerConvertor:
                if param.target not in metas:
                    console.print(
                        f"[red]Error: Target meta '{param.target}' for Parameter '{param.name}' not found.[/red]"
                    )
                    raise SystemExit()

                target_meta = metas[param.target]
                convertor_meta = apply_inner_convertors(param, target_meta)

            if param.convertor:
                convertor_meta = apply_convertor(param, metas)

            if convertor_meta is not None:
                metas[param.name] = convertor_meta

    return metas


def apply_convertor(param: Parameter, temp_metas: Dict[str, str]) -> str:
    convertor_meta = None
    console.print(f"[blue]$[/blue] [yellow]Converting meta for '{param.name}'[/yellow]")
    try:
        convertor_meta = exec_convertor(param.convertor, temp_metas)
    except Exception as e:
        console.print(f"[red] Error converting meta for '{param.name}': {e}[/red]")
        raise SystemExit()

    check_meta_required(param, convertor_meta)

    return convertor_meta


def apply_inner_convertors(param: Parameter, meta: str) -> str:
    convertor_meta = None
    for convertor in param.innerConvertor:
        console.print(
            f"[blue]$[/blue] [yellow]Applying inner convertor '{convertor.name}' for '{param.name}'[/yellow]"
        )
        try:
            convertor_meta = exec_inner_convertor(convertor, meta)
        except Exception as e:
            console.print(
                f"[red]Error applying inner convertor '{convertor.name}' for '{param.name}': {e}[/red]"
            )
            raise SystemExit()

    check_meta_required(param, convertor_meta)

    return convertor_meta


def check_meta_required(param: Parameter, meta: str | None):
    if param.required and meta is None:
        console.print(
            f"[red]Render Error: Parameter '{param.name}' is required but convert to None.[/red]"
        )
        raise SystemExit()


def ask_for_parameter(
    question: str, required: bool, choices: Optional[List[str]]
) -> str:
    if required:
        while True:
            if choices:
                answer: Optional[str] = questionary.select(
                    question, choices=choices
                ).ask()
            else:
                answer: Optional[str] = questionary.text(question, default="").ask()

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
            answer: Optional[str] = questionary.select(
                question, choices=with_empty_choice, default=DEFAULT_NONE_CHOICE
            ).ask()
        else:
            answer: Optional[str] = questionary.text(question, default="").ask()

        if answer is None:
            console.print("[red]Operation cancelled by user.[/red]")
            raise SystemExit()

        return (
            answer.strip()
            if answer.strip() and answer.strip() != DEFAULT_NONE_CHOICE
            else None
        )
