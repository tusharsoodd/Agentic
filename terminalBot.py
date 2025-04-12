import subprocess
import re

def remove_surrounding_quotes(text):
    # Loop to remove all surrounding quotes
    while (text.startswith('`') and text.endswith('`')) or (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    return text

def llm_ask(task):
    # Use Ollama's Gemma2:2B to get a command suggestion
    prompt = (
        f"You are an AI assistant with access to terminal commands. "
        f"Suggest the safest and most efficient terminal commands on Windows to: {task}.\n"
        f"Only provide the commands without any explanations."
        f"Also do not encapsulate the code in quotes or backticks."
    )
    
    # Use the ollama CLI to get the response
    response = subprocess.run(
        ['ollama', 'run', 'gemma2:2b', prompt],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    
    # Clean the response by removing code block markers and extra whitespace
    raw_output = response.stdout.strip()
    print(f"\nRaw LLM response:\n{raw_output}\n")  # Debugging line

    # Extract the commands by removing code block markers and splitting by semicolon
    commands = re.sub(r"```(bash)?", "", raw_output).strip().split('\n')
    commands = [remove_surrounding_quotes(command.strip()) for command in commands]
    return commands

def llm_analyse_response(question, commands, responses):
    # Combine commands and responses into a single string
    combined = "\n".join([f"Command: {cmd}\nResponse: {resp}" for cmd, resp in zip(commands, responses)])
    
    # Use Ollama's Gemma2:2B to get an analysis
    prompt = (
        f"Given this question: {question}\n"
        f"I ran these commands and received these responses on the windows terminal:\n{combined}\n"
        f"How do the commands answer the question? Please answer in one sentence."
    )
    
    # Use the ollama CLI to get the response
    response = subprocess.run(
        ['ollama', 'run', 'gemma2:2b', prompt],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    
    # Clean the response by removing code block markers and extra whitespace
    raw_output = response.stdout.strip()
    print(f"\nAnalysis:\n{raw_output}\n")  # Debugging line

    return raw_output


def execute_command(commands):
    responses = []
    for command in commands:
        print(f"Running command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, 
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("\nOutput:\n", result.stdout)
            responses.append(result.stdout)
        except subprocess.CalledProcessError as e:
            print("\nError:\n", e.stderr)
            responses.append(e.stderr)
            break
    return responses

def main():
    print("Welcome to the Terminal Assistant (Gemma2 Edition)!")
    task = input("What would you like to do? ")
    
    # Ask LLM for a terminal command suggestion
    commands = llm_ask(task)
    print(f"\nSuggested Command: {commands}")
    
    # Get user approval
    approval = input("Do you want to run this command? (yes/no): ").strip().lower()
    if approval == 'yes':
        print("\nRunning command...")
        responses=execute_command(commands)
        analysis=llm_analyse_response(task, commands, responses)
        
    else:
        print("Command not executed.")

if __name__ == "__main__":
    main()
