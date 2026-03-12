# Prompt Library Plan

## Purpose

Define the prompt families the repository expects to own if prompts are part of the system.

## Starter Prompt Families

- execution prompts
- decomposition prompts
- review prompts
- testing prompts
- documentation prompts
- recovery or error prompts

## Rule

If prompts influence runtime behavior, their contracts must stay aligned with:

- actual compiled or executed behavior
- CLI or API surfaces
- recovery expectations
- audit surfaces
