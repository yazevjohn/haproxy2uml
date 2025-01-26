import sys
import re
from pyhaproxy.parse import Parser
from pyhaproxy.render import Render

def haproxy_to_plantuml(config_file):
    # Parse the HAProxy configuration
    parser = Parser(config_file)
    configuration = parser.build_configuration()

    # Start the PlantUML diagram
    plantuml = "@startuml\n\n"

    # Create a class for the global section
    plantuml += "class Global {\n"
    plantuml += "  == configs ==\n"
    for param in configuration.globall.configs():
        plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += "}\n\n"

    # Create a class for the defaults section
    plantuml += "class Defaults {\n"
    for default in configuration.defaults:
        plantuml += f"  == options ==\n"
        for param in default.options():
            plantuml += f"  {param.keyword} {param.value}\n"
        plantuml += f"  == configs ==\n"
        for param in default.configs():
            plantuml += f"  {param.keyword} {param.value}\n"
    plantuml += "}\n\n"

    plantuml += "package Frontends <<Folder>> {\n"
    # Create classes for each frontend
    for frontend in configuration.frontends:
        plantuml += f"class \"{frontend.name}\" {{\n"     
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
    plantuml += "}\n\n"




    # Create classes for each backend
    plantuml += "package Backends <<Folder>> {\n"
    for backend in configuration.backends:
        plantuml += f"class \"{backend.name}\" {{\n"
        plantuml += f"  == options ==\n"
        for param in backend.options():
            plantuml += f"  {param.keyword} {param.value}\n"
        plantuml += f"  == configs ==\n"
        for param in backend.configs():
            plantuml += f"  {param.keyword} {param.value}\n"
        plantuml += f"  == servers ==\n"
        for param in backend.servers():
            plantuml += f"  {param.name} {param.host}:{param.port}\n" #  {param.attributes}
        plantuml += "}\n\n"
    plantuml += "}\n\n"
    
    # Create relationships
    for frontend in configuration.frontends:
        for use_backend in frontend.usebackends():
            if use_backend.is_default:
                plantuml += (
                    f"\"{frontend.name}\" --> \"{use_backend.backend_name}\" #line:green;line.bold;text:green : Default\n"
                )
            else:
                plantuml += (
                    f"\"{frontend.name}\" --> \"{use_backend.backend_name}\" #line.dashed : {use_backend.operator} {use_backend.backend_condition}\n"
                )

    # End the PlantUML diagram
    plantuml += "@enduml"

    return plantuml


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("<haproxy_config_file> not found, try using 'haproxy.cfg'")
        if ('haproxy.cfg'):
            config_file = 'haproxy.cfg'
        else:
            print("Usage: python script.py <haproxy_config_file> or haproxy.cfg")
            sys.exit(1)
    else:
        config_file = sys.argv[1]
    plantuml_diagram = haproxy_to_plantuml(config_file)
    print(plantuml_diagram)
        # Сохранение PlantUML кода в файл
    with open("haproxy_diagram.puml", "w") as f:
        f.write(plantuml_diagram)
