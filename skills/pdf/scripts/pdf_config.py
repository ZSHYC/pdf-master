#!/usr/bin/env python3
"""
PDF Config CLI - AI Provider Configuration Management Tool

Usage:
    pdf-config list              List all providers
    pdf-config show <id>         Show provider details
    pdf-config add               Add a new provider (interactive)
    pdf-config remove <id>       Remove a provider
    pdf-config set-default <id>  Set default provider
    pdf-config test <id>         Test provider connection
"""

import sys
import os
import argparse

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from provider_manager import get_provider_manager, ProviderManager


def cmd_list(args):
    """List all providers"""
    manager = get_provider_manager()
    providers = manager.list_providers()
    default_id = manager.get_default_provider_id()
    
    print("\nAvailable AI Providers:")
    print("=" * 60)
    
    for provider in providers:
        marker = " *" if provider.id == default_id else "  "
        print(f"{marker} {provider.id}")
        print(f"     Name: {provider.name}")
        print(f"     Type: {provider.type}")
        print(f"     Default Model: {provider.get_default_model()}")
        if provider.env_key:
            env_value = os.environ.get(provider.env_key, "(not set)")
            status = "configured" if env_value != "(not set)" else "not configured"
            print(f"     Env Key: {provider.env_key} [{status}]")
        print()
    return 0


def cmd_show(args):
    """Show provider details"""
    manager = get_provider_manager()
    provider = manager.get_provider(args.provider_id)
    
    if not provider:
        print(f"Error: Provider '{args.provider_id}' not found")
        return 1
    
    print(f"\nProvider: {provider.id}")
    print("=" * 60)
    print(f"Name: {provider.name}")
    print(f"Type: {provider.type}")
    print(f"API Base: {provider.api_base or 'N/A'}")
    print(f"Default Model: {provider.get_default_model()}")
    print(f"Cost Multiplier: {provider.cost_multiplier}")
    print(f"Env Key: {provider.env_key or 'N/A'}")
    
    print("\nModels:")
    for model in provider.models:
        print(f"  - {model.id}")
        print(f"      Name: {model.name}")
        print(f"      Max Tokens: {model.max_tokens}")
    
    return 0


def cmd_add(args):
    """Add a new provider"""
    print("\nAdd New Provider")
    print("=" * 60)
    
    provider_id = input("Provider ID (e.g., my-provider): ").strip()
    if not provider_id:
        print("Error: Provider ID is required")
        return 1
    
    name = input(f"Display Name [{provider_id}]: ").strip() or provider_id
    provider_type = input("Type (official/openai-compatible/local) [openai-compatible]: ").strip() or "openai-compatible"
    api_base = input("API Base URL: ").strip()
    env_key = input("Environment Variable Name (optional): ").strip() or None
    
    models = []
    print("\nAdd models (leave empty to finish):")
    while True:
        model_id = input("  Model ID: ").strip()
        if not model_id:
            break
        model_name = input(f"  Model Name [{model_id}]: ").strip() or model_id
        max_tokens = input(f"  Max Tokens [4096]: ").strip() or "4096"
        models.append({
            "id": model_id,
            "name": model_name,
            "max_tokens": int(max_tokens)
        })
    
    if not models:
        print("Error: At least one model is required")
        return 1
    
    default_model = models[0]["id"]
    if len(models) > 1:
        default_model = input(f"Default Model ID [{models[0]['id']}]: ").strip() or models[0]["id"]
    
    cost_multiplier = input("Cost Multiplier [1.0]: ").strip() or "1.0"
    
    config = {
        "id": provider_id,
        "name": name,
        "type": provider_type,
        "api_base": api_base,
        "models": models,
        "default_model": default_model,
        "cost_multiplier": float(cost_multiplier),
        "env_key": env_key,
    }
    
    manager = get_provider_manager()
    if manager.add_provider(config, save=True):
        print(f"\nProvider '{provider_id}' added successfully!")
        return 0
    else:
        print(f"\nError: Failed to add provider")
        return 1


def cmd_remove(args):
    """Remove a provider"""
    manager = get_provider_manager()
    
    if manager.remove_provider(args.provider_id, save=True):
        print(f"Provider '{args.provider_id}' removed successfully!")
        return 0
    else:
        print(f"Error: Failed to remove provider '{args.provider_id}'")
        return 1


def cmd_set_default(args):
    """Set default provider"""
    manager = get_provider_manager()
    
    if manager.set_default(args.provider_id, save=True):
        print(f"Default provider set to '{args.provider_id}'")
        return 0
    else:
        print(f"Error: Provider '{args.provider_id}' not found")
        return 1


def cmd_test(args):
    """Test provider connection"""
    manager = get_provider_manager()
    provider = manager.get_provider(args.provider_id)
    
    if not provider:
        print(f"Error: Provider '{args.provider_id}' not found")
        return 1
    
    print(f"\nTesting provider '{args.provider_id}'...")
    
    if provider.env_key:
        api_key = os.environ.get(provider.env_key)
        if not api_key:
            print(f"  [FAIL] API key not found in environment variable '{provider.env_key}'")
            return 1
        else:
            print(f"  [OK] API key found in environment variable")
    
    try:
        from ai_provider import get_ai_provider
        ai = get_ai_provider(args.provider_id)
        
        if ai.is_available():
            print(f"  [OK] Provider is available")
            
            if args.verbose:
                print(f"  Testing chat...")
                try:
                    response = ai.chat(
                        [{"role": "user", "content": "Say test ok in exactly those words."}],
                        max_tokens=10
                    )
                    print(f"  [OK] Chat test passed: {response.content[:50]}...")
                except Exception as e:
                    print(f"  [WARN] Chat test failed: {e}")
            
            return 0
        else:
            print(f"  [FAIL] Provider is not available")
            return 1
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="PDF Config - AI Provider Configuration Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    subparsers.add_parser("list", help="List all providers")
    
    show_parser = subparsers.add_parser("show", help="Show provider details")
    show_parser.add_argument("provider_id", help="Provider ID")
    
    subparsers.add_parser("add", help="Add a new provider")
    
    remove_parser = subparsers.add_parser("remove", help="Remove a provider")
    remove_parser.add_argument("provider_id", help="Provider ID to remove")
    
    set_default_parser = subparsers.add_parser("set-default", help="Set default provider")
    set_default_parser.add_argument("provider_id", help="Provider ID to set as default")
    
    test_parser = subparsers.add_parser("test", help="Test provider connection")
    test_parser.add_argument("provider_id", help="Provider ID to test")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    commands = {
        "list": cmd_list,
        "show": cmd_show,
        "add": cmd_add,
        "remove": cmd_remove,
        "set-default": cmd_set_default,
        "test": cmd_test,
    }
    
    if args.command in commands:
        return commands[args.command](args) or 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
