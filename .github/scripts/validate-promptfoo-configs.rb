#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "psych"

ROOT = Pathname.new(__dir__).join("..", "..").realpath.freeze
SKILL_IDS = %w[
  chainlink-ccip-skill
  chainlink-cre-skill
  chainlink-data-feeds-skill
  chainlink-data-streams-skill
  chainlink-vrf-skill
  chainlink-ace-skill
].freeze
HELPER_REQUIRE = 'require("../../shared/with-skill-prompt")'.freeze

abort "Usage: ruby .github/scripts/validate-promptfoo-configs.rb references" unless ARGV == ["references"]

failures = []

def report(failures, context, message)
  failures << "#{context}: #{message}"
end

def validate_prompt_script(root, skill_id, failures)
  prompt_path = root.join("evals", skill_id, "prompts", "with-skill.js")
  context = prompt_path.relative_path_from(root)
  source = prompt_path.read

  report(failures, context, "must use the shared with-skill prompt helper") unless source.include?(HELPER_REQUIRE)
  report(failures, context, "must not read files directly") if source.match?(/readFile(?:Sync)?\s*\(/)
end

def validate_reference_path(root, skill_root, reference_file, context, failures)
  unless reference_file.is_a?(String) && !reference_file.empty?
    report(failures, context, "reference_files entries must be non-empty strings")
    return
  end

  candidate = Pathname.new(reference_file)
  if candidate.absolute?
    report(failures, context, "reference path must be relative: #{reference_file.inspect}")
    return
  end

  resolved = skill_root.join(candidate).cleanpath
  unless resolved.to_s.start_with?("#{skill_root}/")
    report(failures, context, "reference path escapes skill directory: #{reference_file.inspect}")
    return
  end

  unless resolved.file?
    report(failures, context, "reference file does not exist: #{reference_file.inspect}")
    return
  end

  canonical = resolved.realpath
  unless canonical.to_s.start_with?("#{skill_root}/")
    report(failures, context, "reference path escapes skill directory through a symlink: #{reference_file.inspect}")
  end
end

SKILL_IDS.each do |skill_id|
  config_path = ROOT.join("evals", skill_id, "promptfooconfig.yaml")
  skill_root = ROOT.join(skill_id).realpath
  config = Psych.safe_load(config_path.read, aliases: true)
  tests = config.fetch("tests")

  validate_prompt_script(ROOT, skill_id, failures)

  tests.each_with_index do |test, index|
    context = "#{config_path.relative_path_from(ROOT)} test #{index + 1} (#{test.fetch("description", "unnamed")})"
    vars = test["vars"]
    unless vars.is_a?(Hash)
      report(failures, context, "must define vars")
      next
    end

    unless vars.key?("reference_files") && vars["reference_files"].is_a?(Array)
      report(failures, context, "vars.reference_files must be an array")
      next
    end

    references = vars["reference_files"]
    report(failures, context, "vars.reference_files must not contain duplicate paths") unless references.uniq.length == references.length
    references.each { |reference_file| validate_reference_path(ROOT, skill_root, reference_file, context, failures) }
  end
end

if failures.empty?
  puts "Promptfoo reference metadata is valid."
  exit 0
end

warn failures.join("\n")
exit 1
