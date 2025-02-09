import sys
import argparse
import os
import re
from pyhaproxy.parse import Parser
from pyhaproxy.render import Render


def create_class_defaults(configuration):
    # Create a class for the defaults section
    plantuml = "class Defaults {\n"
    for default in configuration.defaults:
        plantuml += f"  == options ==\n"
        for param in default.options():
            plantuml += f"  {param.keyword} {param.value}\n"
        plantuml += f"  == configs ==\n"
        for param in default.configs():
            plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += "}\n\n"

    return plantuml


def create_class_global(configuration):
    # Create a class for the global section
    plantuml = "class Global {\n"
    plantuml += "  == configs ==\n"
    for param in configuration.globall.configs():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += "}\n\n"

    return plantuml


def create_frontend_class(frontend: str):
    # Create a class for each frontend
    plantuml = f'class "{frontend.name}" {{\n'
    plantuml += f"  == bind ==\n"
    plantuml += f"host:  {frontend.host}\n"
    plantuml += f"port:  {frontend.port}\n"
    plantuml += f"  == options ==\n"
    for param in frontend.options():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += f"  == configs ==\n"
    for param in frontend.configs():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += "}\n\n"
    return plantuml


def create_classes_for_frontends(configuration, frontend_filter: str):
    # Create classes for each frontend
    plantuml = "package Frontends <<Folder>> {\n"
    if configuration.frontend(frontend_filter):
        plantuml += create_frontend_class(configuration.frontend(frontend_filter))
    else:
        for frontend in configuration.frontends:
            plantuml += create_frontend_class(frontend)
    plantuml += "}\n\n"

    return plantuml


def create_backend_class(backend: str):
    # Create a class for each backend
    plantuml = f'class "{backend.name}" {{\n'
    plantuml += f"  == options ==\n"
    for param in backend.options():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += f"  == configs ==\n"
    for param in backend.configs():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += f"  == servers ==\n"
    for param in backend.servers():
        plantuml += f"  {param.name} {param.host}:{param.port}\n"  #  {param.attributes}
    plantuml += "}\n\n"
    return plantuml


def create_classes_for_backends(configuration):
    # Create classes for each backend
    plantuml = "package Backends <<Folder>> {\n"
    for backend in configuration.backends:
        plantuml += create_backend_class(backend)
    plantuml += "}\n\n"

    return plantuml


def create_relationships(configuration):
    # Create relationships
    plantuml = ""
    for frontend in configuration.frontends:
        if frontend.name == frontend_filter:
            for use_backend in frontend.usebackends():
                if use_backend.is_default:
                    plantuml += f'"{frontend.name}" --> "{use_backend.backend_name}" #line:green;line.bold;text:green : Default\n'
                else:
                    plantuml += f'"{frontend.name}" --> "{use_backend.backend_name}" #line.dashed : {use_backend.operator} {use_backend.backend_condition}\n'

    return plantuml


def haproxy_to_plantuml(config_file):
    # Parse the HAProxy configuration
    parser = Parser(config_file)
    configuration = parser.build_configuration()

    # Start the PlantUML diagram
    plantuml = "@startuml\n\n"

    plantuml += create_class_global(configuration)
    plantuml += create_class_defaults(configuration)
    plantuml += create_classes_for_frontends(configuration, frontend_filter)
    plantuml += create_classes_for_backends(configuration)
    plantuml += create_relationships(configuration)

    # End the PlantUML diagram
    plantuml += "@enduml"

    return plantuml


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", help="Путь к конфигу HAProxy", required=True)
    parser.add_argument("--frontend", help="Фильтр по frontend")
    parser.add_argument("--backend", help="Фильтр по backend")
    try:
        parsed_args = parser.parse_args(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))
    return parsed_args


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if not os.path.exists(args.config_file):
        print(f"Файл конфигурации '{args.config_file}' не найден")
        sys.exit(1)
    else:
        config_file = args.config_file
    frontend_filter = args.frontend
    plantuml_diagram = haproxy_to_plantuml(config_file)
    print(plantuml_diagram)
    # Сохранение PlantUML кода в файл
    with open("haproxy_diagram.puml", "w") as f:
        f.write(plantuml_diagram)
