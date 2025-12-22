"""Parser for Home Assistant automation YAML files."""
import logging
from typing import List, Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


class AutomationParser:
    """Parser for Home Assistant automation YAML files."""
    
    @staticmethod
    def parse_automation_file(content: str) -> List[Dict[str, Any]]:
        """
        Parse a YAML file containing Home Assistant automations.
        
        This is a best-effort parser that extracts automation metadata.
        It handles various YAML structures gracefully.
        
        Args:
            content: YAML file content as string
            
        Returns:
            List of automation dictionaries with extracted metadata
        """
        automations = []
        
        try:
            # Parse YAML content
            data = yaml.safe_load(content)
            
            if data is None:
                logger.warning("Empty YAML content")
                return automations
            
            # Handle different YAML structures
            if isinstance(data, list):
                # Direct list of automations
                automations_list = data
            elif isinstance(data, dict):
                # Could be wrapped in a key, or a single automation
                if "automation" in data:
                    automations_list = data["automation"]
                    if not isinstance(automations_list, list):
                        automations_list = [automations_list]
                else:
                    # Treat the whole dict as a single automation
                    automations_list = [data]
            else:
                logger.warning(f"Unexpected YAML structure: {type(data)}")
                return automations
            
            # Extract metadata from each automation
            for idx, auto in enumerate(automations_list):
                if not isinstance(auto, dict):
                    logger.warning(f"Skipping non-dict automation at index {idx}")
                    continue
                
                parsed = AutomationParser._parse_single_automation(auto)
                if parsed:
                    automations.append(parsed)
            
            logger.info(f"Parsed {len(automations)} automations from YAML")
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing automations: {e}")
        
        return automations
    
    @staticmethod
    def _parse_single_automation(automation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a single automation dictionary.
        
        Args:
            automation: Dictionary representing one automation
            
        Returns:
            Parsed automation metadata, or None if invalid
        """
        try:
            # Extract alias/name (required for meaningful display)
            alias = automation.get("alias") or automation.get("name") or automation.get("id")
            
            # Extract description
            description = automation.get("description", "")
            
            # Extract trigger types (best effort)
            trigger_types = AutomationParser._extract_trigger_types(automation.get("trigger", []))
            
            return {
                "alias": alias,
                "description": description,
                "trigger_types": trigger_types,
            }
            
        except Exception as e:
            logger.warning(f"Error parsing single automation: {e}")
            return None
    
    @staticmethod
    def _extract_trigger_types(triggers: Any) -> List[str]:
        """
        Extract trigger types from automation triggers.
        
        Triggers can be a single dict or a list of dicts.
        Each trigger typically has a 'platform' key.
        
        Args:
            triggers: Trigger configuration (dict or list)
            
        Returns:
            List of unique trigger types
        """
        trigger_types = []
        
        try:
            # Normalize to list
            if isinstance(triggers, dict):
                triggers = [triggers]
            elif not isinstance(triggers, list):
                return trigger_types
            
            # Extract platform from each trigger
            for trigger in triggers:
                if isinstance(trigger, dict):
                    platform = trigger.get("platform")
                    if platform and platform not in trigger_types:
                        trigger_types.append(platform)
        
        except Exception as e:
            logger.warning(f"Error extracting trigger types: {e}")
        
        return trigger_types
