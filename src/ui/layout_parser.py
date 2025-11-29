import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
import os

class LayoutParser:
    def __init__(self, theme_config: Dict[str, Any] = None, layout_dir: str = "src/ui/layouts"):
        self.layout_dir = layout_dir
        self.theme_config = theme_config or {}
        self.main_layout = None  # The unified main.xml root
        self.file_timestamp = 0
        self.current_mode_name = "default"
        self._id_cache: Dict[str, Dict[str, Any]] = {}  # Cache per mode
        self._config_cache: Dict[str, Dict[str, Any]] = {}  # Cache per mode
        self._style_cache: Dict[str, Any] = {}  # Global style variables
        self._animation_cache: Dict[str, Any] = {}  # Global animations
        self._template_cache: Dict[str, Any] = {}  # Templates for reuse
        self._behavior_cache: Dict[str, Dict[str, Any]] = {}  # Behavior config per mode
        self._text_style_cache: Dict[str, Dict[str, Any]] = {}  # Text styles
        self._border_style_cache: Dict[str, Dict[str, Any]] = {}  # Border styles
        self._menu_cache: Dict[str, Dict[str, Any]] = {}  # Menu definitions
        self._stats_cache: Dict[str, Any] = {}  # Stats configuration
        self._global_config: Dict[str, Any] = {}  # Global config (icon_aliases, modes, mode_colors)
        self._layouts_cache: Dict[str, Dict[str, Any]] = {}  # Layout definitions (multi_column, etc.)
        self._mode_overrides_cache: Dict[str, Dict[str, Any]] = {}  # Per-mode style overrides
        self._component_cache: Dict[str, Dict[str, Any]] = {}  # Component primitives
        self._slots_cache: Dict[str, Dict[str, Any]] = {}  # Data slot definitions
        self._overlays_cache: Dict[str, Dict[str, Any]] = {}  # Overlay definitions
        self._formatters_cache: Dict[str, Dict[str, Any]] = {}  # Value formatters
        
        # For backwards compatibility - track "old" layouts too
        self.layouts: Dict[str, Any] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.current_layout_name = "default"
        
        # Try to load unified main.xml first, fallback to individual files
        self._load_main_layout()
    
    def _load_main_layout(self) -> bool:
        """Load the unified main.xml layout file."""
        path = os.path.join(self.layout_dir, "main.xml")
        
        if not os.path.exists(path):
            # Fallback to loading default.xml
            self._load_layout("default")
            return False
        
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.main_layout = root
            self.file_timestamp = os.path.getmtime(path)
            
            # Parse global style element
            style_elem = root.find('style')
            if style_elem is not None:
                self._parse_global_style(style_elem)
            
            # Parse templates
            for template_elem in root.findall('template'):
                template_id = template_elem.get('id')
                if template_id:
                    self._template_cache[template_id] = template_elem
            
            # Parse global config (fallback defaults + icon_aliases, modes, mode_colors)
            config_elem = root.find('config')
            if config_elem is not None:
                self._parse_global_config(config_elem)
                self._parse_config_for_mode("default", config_elem)
            
            # Parse menus
            menus_elem = root.find('menus')
            if menus_elem is not None:
                self._parse_menus(menus_elem)
            
            # Parse stats config
            stats_elem = root.find('stats')
            if stats_elem is not None:
                self._parse_stats(stats_elem)
            
            # Parse layouts section (new unified approach)
            layouts_elem = root.find('layouts')
            if layouts_elem is not None:
                self._parse_layouts(layouts_elem)
            
            # Parse mode_overrides section
            mode_overrides_elem = root.find('mode_overrides')
            if mode_overrides_elem is not None:
                self._parse_mode_overrides(mode_overrides_elem)
            
            # Parse slots section
            slots_elem = root.find('slots')
            if slots_elem is not None:
                self._parse_slots(slots_elem)
            
            # Parse overlays section
            overlays_elem = root.find('overlays')
            if overlays_elem is not None:
                self._parse_overlays(overlays_elem)
            
            # Parse templates section (look for <templates> wrapper too)
            templates_elem = root.find('templates')
            if templates_elem is not None:
                for template_elem in templates_elem.findall('template'):
                    template_id = template_elem.get('id')
                    if template_id:
                        self._template_cache[template_id] = template_elem
            
            # Parse each mode (legacy support)
            for mode_elem in root.findall('mode'):
                mode_name = mode_elem.get('name')
                if mode_name:
                    self._parse_mode(mode_name, mode_elem)
            
            print(f"Loaded unified layout: main.xml")
            return True
        except Exception as e:
            print(f"Error loading main.xml: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to loading default.xml
            self._load_layout("default")
            return False

    def _parse_global_style(self, style_elem):
        """Parse global style element for variables, animations, text and border styles."""
        # Parse var elements
        for var_elem in style_elem.findall('var'):
            var_name = var_elem.get('name')
            var_value = var_elem.get('value')
            if var_name and var_value:
                if var_value.startswith('@'):
                    resolved = self._resolve_theme_variable(var_value[1:])
                    if resolved is not None:
                        self._style_cache[var_name] = resolved
                    else:
                        self._style_cache[var_name] = var_value
                else:
                    self._style_cache[var_name] = self._parse_value(var_value)
        
        # Parse animation elements
        for anim_elem in style_elem.findall('animation'):
            anim_name = anim_elem.get('name')
            if anim_name:
                duration = anim_elem.get('duration', '100')
                if isinstance(duration, str) and duration.startswith('@'):
                    resolved = self._resolve_theme_variable(duration[1:])
                    duration = resolved if resolved is not None else 100
                else:
                    duration = self._parse_value(duration)
                
                self._animation_cache[anim_name] = {
                    'duration': int(duration) if duration else 100,
                    'easing': anim_elem.get('easing', 'linear')
                }
        
        # Parse text styles
        for text_elem in style_elem.findall('text'):
            text_name = text_elem.get('name')
            if text_name:
                self._text_style_cache[text_name] = self._parse_attributes(text_elem.attrib)
        
        # Parse border styles
        for border_elem in style_elem.findall('border'):
            border_name = border_elem.get('name')
            if border_name:
                self._border_style_cache[border_name] = self._parse_attributes(border_elem.attrib)

    def _parse_menus(self, menus_elem):
        """Parse menu definitions from XML."""
        for menu_elem in menus_elem.findall('menu'):
            menu_name = menu_elem.get('name')
            if not menu_name:
                continue
            
            menu_data = {
                'name': menu_name,
                'displayname': menu_elem.get('displayname', menu_name.title()),
                'icon': menu_elem.get('icon'),
                'type': menu_elem.get('type', 'list'),
                'options': []
            }
            
            # Check if it's an action menu (like gallery)
            if menu_data['type'] == 'action':
                menu_data['action'] = menu_elem.get('action')
            else:
                # Parse items and groups
                menu_data['options'] = self._parse_menu_items(menu_elem)
            
            self._menu_cache[menu_name] = menu_data

    def _parse_menu_items(self, parent_elem) -> List[Dict[str, Any]]:
        """Parse menu items and groups from an element."""
        items = []
        
        for child in parent_elem:
            if child.tag == 'item':
                item = self._parse_menu_item(child)
                if item:
                    items.append(item)
            elif child.tag == 'group':
                group = self._parse_menu_group(child)
                if group:
                    items.append(group)
        
        return items

    def _parse_menu_item(self, item_elem) -> Dict[str, Any]:
        """Parse a single menu item."""
        item_type = item_elem.get('type', 'list')
        
        item = {
            'name': item_elem.get('name'),
            'displayname': item_elem.get('displayname', item_elem.get('name', '').title()),
            'type': item_type,
            'style': item_elem.get('style'),
            'format': item_elem.get('format')
        }
        
        if item_type == 'range':
            item['options'] = {
                'min': self._parse_value(item_elem.get('min', '0')),
                'max': self._parse_value(item_elem.get('max', '100')),
                'step': self._parse_value(item_elem.get('step', '1'))
            }
            item['value'] = self._parse_value(item_elem.get('value', '0'))
        elif item_type == 'list':
            item['options'] = []
            for option_elem in item_elem.findall('option'):
                opt = {
                    'value': self._parse_value(option_elem.get('value')),
                    'displayname': option_elem.get('displayname', str(option_elem.get('value'))),
                    'style': option_elem.get('style')
                }
                item['options'].append(opt)
            item['value'] = self._parse_value(item_elem.get('value'))
        elif item_type == 'action':
            item['action'] = item_elem.get('action')
        
        return item

    def _parse_menu_group(self, group_elem) -> Dict[str, Any]:
        """Parse a menu group (submenu container)."""
        group = {
            'name': group_elem.get('name'),
            'displayname': group_elem.get('displayname', group_elem.get('name', '').title()),
            'type': 'list',
            'options': self._parse_menu_items(group_elem)
        }
        return group

    def _parse_stats(self, stats_elem):
        """Parse stats configuration."""
        self._stats_cache = {
            'modes': {},
            'available': [],
            'display': {'left': [], 'right': []}
        }
        
        # Parse mode-specific stats
        modes_elem = stats_elem.find('modes')
        if modes_elem is not None:
            for mode_elem in modes_elem.findall('mode'):
                mode_name = mode_elem.get('name')
                stats_str = mode_elem.get('stats', '')
                if mode_name:
                    self._stats_cache['modes'][mode_name] = [s.strip() for s in stats_str.split(',') if s.strip()]
        
        # Parse available stats
        available_elem = stats_elem.find('available')
        if available_elem is not None and available_elem.text:
            self._stats_cache['available'] = [s.strip() for s in available_elem.text.split(',') if s.strip()]
        
        # Parse display positions
        display_elem = stats_elem.find('display')
        if display_elem is not None:
            left_elem = display_elem.find('left')
            if left_elem is not None and left_elem.text:
                self._stats_cache['display']['left'] = [s.strip() for s in left_elem.text.split(',') if s.strip()]
            right_elem = display_elem.find('right')
            if right_elem is not None and right_elem.text:
                self._stats_cache['display']['right'] = [s.strip() for s in right_elem.text.split(',') if s.strip()]

    def _parse_layouts(self, layouts_elem):
        """Parse layout definitions from the <layouts> section."""
        for layout_elem in layouts_elem.findall('layout'):
            layout_name = layout_elem.get('name')
            if not layout_name:
                continue
            
            layout_data = {
                'name': layout_name,
                'type': layout_elem.get('type', 'multi_column'),
                'columns': {},
                'config': {},
                'footer': None,
                'content': None
            }
            
            # Parse config (like auto_collapse behavior)
            config_elem = layout_elem.find('config')
            if config_elem is not None:
                behavior_elem = config_elem.find('behavior')
                if behavior_elem is not None:
                    layout_data['config']['behavior'] = self._parse_attributes(behavior_elem.attrib)
            
            # Parse columns
            columns_elem = layout_elem.find('columns')
            if columns_elem is not None:
                for column_elem in columns_elem.findall('column'):
                    col_id = column_elem.get('id')
                    col_level = column_elem.get('level', '0')
                    if col_id:
                        col_data = {
                            'id': col_id,
                            'level': int(col_level),
                            'expanded': {},
                            'collapsed': {},
                            'collapse_when': None,
                            'visible_when': None,
                            'style': {},
                            'collapsed_style': {},
                            'range_style': {}
                        }
                        
                        # Parse expanded/collapsed widths
                        expanded_elem = column_elem.find('expanded')
                        if expanded_elem is not None:
                            width = expanded_elem.get('width')
                            if width:
                                col_data['expanded']['width'] = self._resolve_style_value(width)
                        
                        collapsed_elem = column_elem.find('collapsed')
                        if collapsed_elem is not None:
                            width = collapsed_elem.get('width')
                            if width:
                                col_data['collapsed']['width'] = self._resolve_style_value(width)
                        
                        # Parse conditions
                        collapse_when = column_elem.find('collapse_when')
                        if collapse_when is not None and collapse_when.text:
                            col_data['collapse_when'] = collapse_when.text.strip()
                        
                        visible_when = column_elem.find('visible_when')
                        if visible_when is not None and visible_when.text:
                            col_data['visible_when'] = visible_when.text.strip()
                        
                        # Parse styles
                        style_elem = column_elem.find('style')
                        if style_elem is not None:
                            col_data['style'] = self._parse_attributes(style_elem.attrib)
                        
                        collapsed_style_elem = column_elem.find('collapsed_style')
                        if collapsed_style_elem is not None:
                            col_data['collapsed_style'] = self._parse_attributes(collapsed_style_elem.attrib)
                        
                        range_style_elem = column_elem.find('range_style')
                        if range_style_elem is not None:
                            col_data['range_style'] = self._parse_attributes(range_style_elem.attrib)
                        
                        layout_data['columns'][col_id] = col_data
            
            # Parse footer
            footer_elem = layout_elem.find('footer')
            if footer_elem is not None:
                use_elem = footer_elem.find('use')
                if use_elem is not None:
                    layout_data['footer'] = {'template': use_elem.get('template')}
            
            # Parse content (for gallery layout, etc.)
            content_elem = layout_elem.find('content')
            if content_elem is not None:
                layout_data['content'] = []
                for container_elem in content_elem.findall('container'):
                    layout_data['content'].append(self._parse_attributes(container_elem.attrib))
            
            self._layouts_cache[layout_name] = layout_data
            
            # Also create config cache entry for this layout for backwards compatibility
            if layout_name not in self._config_cache:
                self._create_config_from_layout(layout_name, layout_data)

    def _create_config_from_layout(self, layout_name: str, layout_data: Dict[str, Any]):
        """Create a config cache entry from a layout definition."""
        config = {
            'widths': {},
            'animation': self._animation_cache.get('menu_transition', {'duration': 100, 'easing': 'ease-out'})
        }
        
        # Extract widths from columns
        for col_id, col_data in layout_data.get('columns', {}).items():
            expanded_width = col_data.get('expanded', {}).get('width')
            collapsed_width = col_data.get('collapsed', {}).get('width')
            
            if expanded_width:
                config['widths'][col_id] = expanded_width
            if collapsed_width:
                config['widths']['collapsed'] = collapsed_width
        
        # Set behavior from config
        behavior = layout_data.get('config', {}).get('behavior', {})
        if behavior:
            self._behavior_cache[layout_name] = behavior
        
        self._config_cache[layout_name] = config

    def _resolve_style_value(self, value: str) -> Any:
        """Resolve a style value that might be a @variable reference."""
        if isinstance(value, str) and value.startswith('@'):
            var_name = value[1:]
            if var_name in self._style_cache:
                return self._style_cache[var_name]
            resolved = self._resolve_theme_variable(var_name)
            if resolved is not None:
                return resolved
        return self._parse_value(value)

    def _parse_mode_overrides(self, overrides_elem):
        """Parse mode-specific style overrides."""
        for mode_elem in overrides_elem.findall('mode'):
            mode_name = mode_elem.get('name')
            if not mode_name:
                continue
            
            override_data = {
                'columns': {},
                'widths': {}
            }
            
            # Parse column overrides
            for column_elem in mode_elem.findall('column'):
                col_id = column_elem.get('id')
                context = column_elem.get('context')  # e.g., "danger" for system reset
                
                if col_id:
                    key = f"{col_id}:{context}" if context else col_id
                    style_elem = column_elem.find('style')
                    if style_elem is not None:
                        override_data['columns'][key] = self._parse_attributes(style_elem.attrib)
            
            # Parse width overrides
            widths_elem = mode_elem.find('widths')
            if widths_elem is not None:
                for key in ['level_0', 'level_1', 'level_2', 'collapsed']:
                    val = widths_elem.get(key)
                    if val:
                        override_data['widths'][key] = self._resolve_style_value(val)
            
            self._mode_overrides_cache[mode_name] = override_data
            
            # Also update config cache with these widths
            if override_data['widths']:
                if mode_name not in self._config_cache:
                    self._config_cache[mode_name] = {'widths': {}, 'animation': self._animation_cache.get('menu_transition', {'duration': 100, 'easing': 'ease-out'})}
                self._config_cache[mode_name]['widths'].update(override_data['widths'])

    def _parse_global_config(self, config_elem):
        """Parse global configuration (icon_aliases, modes, mode_colors, icons, formatters, etc.)."""
        self._global_config = {
            'icon_aliases': {},
            'modes': ['auto', 'manual', 'timelapse'],  # Default
            'mode_colors': {
                'auto': '#00FFFF',
                'manual': '#FFC864',
                'timelapse': '#64FF64'
            },
            'icons': {
                'path': 'src/ui/icons',
                'extension': '.svg'
            },
            'text_scroll': {
                'speed': 0.05,
                'pause_ms': 1000
            },
            'navigation': {
                'wrap_menus': True,
                'wrap_items': True,
                'auto_collapse_delay': 0
            },
            'startup': {
                'show_stats': True,
                'show_menu': False,
                'splash_duration': 2000,
                'splash_fade': 500
            }
        }
        
        # Parse modes list
        modes_elem = config_elem.find('modes')
        if modes_elem is not None and modes_elem.text:
            self._global_config['modes'] = [m.strip() for m in modes_elem.text.split(',') if m.strip()]
        
        # Parse icon aliases
        aliases_elem = config_elem.find('icon_aliases')
        if aliases_elem is not None:
            for alias_elem in aliases_elem.findall('alias'):
                from_name = alias_elem.get('from')
                to_name = alias_elem.get('to')
                if from_name and to_name:
                    self._global_config['icon_aliases'][from_name] = to_name
        
        # Parse mode colors
        colors_elem = config_elem.find('mode_colors')
        if colors_elem is not None:
            for color_elem in colors_elem.findall('color'):
                mode = color_elem.get('mode')
                value = color_elem.get('value')
                if mode and value:
                    self._global_config['mode_colors'][mode] = value
        
        # Parse icons config
        icons_elem = config_elem.find('icons')
        if icons_elem is not None:
            self._global_config['icons']['path'] = icons_elem.get('path', 'src/ui/icons')
            self._global_config['icons']['extension'] = icons_elem.get('extension', '.svg')
        
        # Parse text scroll config
        scroll_elem = config_elem.find('text_scroll')
        if scroll_elem is not None:
            speed = scroll_elem.get('speed')
            if speed:
                self._global_config['text_scroll']['speed'] = float(speed)
            pause = scroll_elem.get('pause_ms')
            if pause:
                self._global_config['text_scroll']['pause_ms'] = int(pause)
        
        # Parse navigation config
        nav_elem = config_elem.find('navigation')
        if nav_elem is not None:
            wrap_menus = nav_elem.find('wrap_menus')
            if wrap_menus is not None and wrap_menus.text:
                self._global_config['navigation']['wrap_menus'] = wrap_menus.text.lower() == 'true'
            wrap_items = nav_elem.find('wrap_items')
            if wrap_items is not None and wrap_items.text:
                self._global_config['navigation']['wrap_items'] = wrap_items.text.lower() == 'true'
            collapse_delay = nav_elem.find('auto_collapse_delay')
            if collapse_delay is not None and collapse_delay.text:
                self._global_config['navigation']['auto_collapse_delay'] = int(collapse_delay.text)
        
        # Parse startup config
        startup_elem = config_elem.find('startup')
        if startup_elem is not None:
            show_stats = startup_elem.find('show_stats')
            if show_stats is not None and show_stats.text:
                self._global_config['startup']['show_stats'] = show_stats.text.lower() == 'true'
            show_menu = startup_elem.find('show_menu')
            if show_menu is not None and show_menu.text:
                self._global_config['startup']['show_menu'] = show_menu.text.lower() == 'true'
            splash_duration = startup_elem.find('splash_duration')
            if splash_duration is not None and splash_duration.text:
                self._global_config['startup']['splash_duration'] = int(splash_duration.text)
            splash_fade = startup_elem.find('splash_fade')
            if splash_fade is not None and splash_fade.text:
                self._global_config['startup']['splash_fade'] = int(splash_fade.text)
        
        # Parse formatters
        formatters_elem = config_elem.find('formatters')
        if formatters_elem is not None:
            for fmt_elem in formatters_elem.findall('format'):
                key = fmt_elem.get('key')
                if key:
                    self._formatters_cache[key] = {
                        'type': fmt_elem.get('type', 'string'),
                        'separator': fmt_elem.get('separator', ''),
                        'prefix': fmt_elem.get('prefix', ''),
                        'suffix': fmt_elem.get('suffix', '')
                    }

    def _parse_slots(self, slots_elem):
        """Parse data slot definitions."""
        for slot_elem in slots_elem.findall('slot'):
            slot_name = slot_elem.get('name')
            if slot_name:
                self._slots_cache[slot_name] = {
                    'name': slot_name,
                    'type': slot_elem.get('type', 'string'),
                    'default': self._parse_value(slot_elem.get('default')),
                    'description': slot_elem.get('description', '')
                }

    def _parse_overlays(self, overlays_elem):
        """Parse overlay definitions."""
        for overlay_elem in overlays_elem.findall('overlay'):
            overlay_id = overlay_elem.get('id')
            if overlay_id:
                # Parse all attributes directly from overlay element
                overlay_data = self._parse_attributes(overlay_elem.attrib)
                overlay_data['id'] = overlay_id
                overlay_data['containers'] = []
                
                # Convert numeric strings for position/sizing (if not already converted and not percentage)
                for key in ['x', 'y', 'font_size', 'shadow_offset']:
                    if key in overlay_data:
                        val = overlay_data[key]
                        if isinstance(val, str) and not val.endswith('%'):
                            try:
                                overlay_data[key] = int(val)
                            except ValueError:
                                pass
                
                for container_elem in overlay_elem.findall('container'):
                    overlay_data['containers'].append(self._parse_attributes(container_elem.attrib))
                    
                    # Parse nested elements (text, etc.)
                    for child in container_elem:
                        if child.tag == 'text':
                            overlay_data['containers'][-1]['text'] = self._parse_attributes(child.attrib)
                            overlay_data['containers'][-1]['text']['content'] = child.get('content', '')
                
                self._overlays_cache[overlay_id] = overlay_data

    def _parse_mode(self, mode_name: str, mode_elem):
        """Parse a mode element and cache its containers."""
        # Initialize caches for this mode
        self._id_cache[mode_name] = {}
        
        # Parse mode-specific config
        config_elem = mode_elem.find('config')
        if config_elem is not None:
            self._parse_config_for_mode(mode_name, config_elem)
            
            # Parse behavior element
            behavior_elem = config_elem.find('behavior')
            if behavior_elem is not None:
                self._behavior_cache[mode_name] = self._parse_attributes(behavior_elem.attrib, mode_name)
        
        # Parse containers
        for container_elem in mode_elem.findall('container'):
            eid = container_elem.get('id')
            if eid:
                self._id_cache[mode_name][eid] = self._parse_attributes(container_elem.attrib, mode_name)
        
        # Handle <use template="..."> elements - copy template containers
        for use_elem in mode_elem.findall('use'):
            template_name = use_elem.get('template')
            if template_name and template_name in self._template_cache:
                template = self._template_cache[template_name]
                for container_elem in template.findall('container'):
                    eid = container_elem.get('id')
                    if eid:
                        self._id_cache[mode_name][eid] = self._parse_attributes(container_elem.attrib, mode_name)

    def _parse_config_for_mode(self, mode_name: str, config_elem):
        """Parse config element for a specific mode."""
        config = {}
        
        # Get defaults from theme config
        sizes = self.theme_config.get("theme", {}).get("sizes", {})
        if not sizes:
            sizes = self.theme_config.get("sizes", {})
        default_widths = {
            'level_0': sizes.get('level_0_width', 200),
            'level_1': sizes.get('level_1_width', 260),
            'level_2': sizes.get('level_2_width', 260),
            'collapsed': sizes.get('collapsed_width', 60)
        }
        
        widths_elem = config_elem.find('widths')
        if widths_elem is not None:
            config['widths'] = {}
            for key in ['level_0', 'level_1', 'level_2', 'collapsed']:
                val = widths_elem.get(key, str(default_widths.get(key, 200)))
                if isinstance(val, str) and val.startswith('@'):
                    resolved = self._resolve_theme_variable(val[1:])
                    config['widths'][key] = int(resolved) if resolved is not None else default_widths.get(key, 200)
                else:
                    config['widths'][key] = int(val)
        else:
            config['widths'] = default_widths
        
        # Animation
        default_animation = 100
        if "display" in self.theme_config:
            default_animation = self.theme_config["display"].get("animation_duration", 100)
        
        anim_elem = config_elem.find('animation')
        if anim_elem is not None:
            duration_val = anim_elem.get('duration', str(default_animation))
            if isinstance(duration_val, str) and duration_val.startswith('@'):
                resolved = self._resolve_theme_variable(duration_val[1:])
                duration = int(resolved) if resolved is not None else default_animation
            else:
                duration = int(duration_val)
            config['animation'] = {'duration': duration}
        else:
            config['animation'] = {'duration': default_animation}
        
        self._config_cache[mode_name] = config

    def get_theme_value(self, category: str, key: str, default: Any = None) -> Any:
        """Get a value from the theme config (colors or sizes)."""
        if category in self.theme_config and key in self.theme_config[category]:
            return self.theme_config[category][key]
        return default

    def _resolve_theme_variable(self, var_name: str) -> Any:
        """Resolve a @variable reference from theme_config."""
        # Search in theme.colors (nested structure from settings)
        if "theme" in self.theme_config:
            theme = self.theme_config["theme"]
            if "colors" in theme and var_name in theme["colors"]:
                return theme["colors"][var_name]
            if "sizes" in theme and var_name in theme["sizes"]:
                return theme["sizes"][var_name]
        # Search in top-level colors (if theme_config is just the theme dict)
        if "colors" in self.theme_config and var_name in self.theme_config["colors"]:
            return self.theme_config["colors"][var_name]
        # Search in top-level sizes
        if "sizes" in self.theme_config and var_name in self.theme_config["sizes"]:
            return self.theme_config["sizes"][var_name]
        # Search in display (for animation_duration etc)
        if "display" in self.theme_config and var_name in self.theme_config["display"]:
            return self.theme_config["display"][var_name]
        return None

    def load_layout(self, layout_name: str):
        """Switch to a specific mode/layout."""
        normalized_name = layout_name.lower().replace(" ", "_")
        
        # If using unified layout and mode exists
        if self.main_layout is not None and normalized_name in self._id_cache:
            self.current_mode_name = normalized_name
            self.current_layout_name = normalized_name
            return
        
        # Fallback to loading individual file (backwards compat)
        if normalized_name not in self.layouts:
            if not self._load_layout(normalized_name):
                self.current_layout_name = "default"
                self.current_mode_name = "default"
                return
        
        self.current_layout_name = normalized_name
        self.current_mode_name = normalized_name

    def _load_layout(self, name: str) -> bool:
        """Load an individual layout file (backwards compatibility)."""
        filename = f"{name}.xml"
        path = os.path.join(self.layout_dir, filename)
        
        if not os.path.exists(path):
            return False
            
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.layouts[name] = root
            self.file_timestamps[name] = os.path.getmtime(path)
            
            # Initialize caches
            if name not in self._id_cache:
                self._id_cache[name] = {}
            if name not in self._config_cache:
                self._config_cache[name] = {}
            
            # Parse style
            style_elem = root.find('style')
            if style_elem is not None:
                self._parse_global_style(style_elem)
            
            # Parse config
            config_elem = root.find('config')
            if config_elem is not None:
                self._parse_config_for_mode(name, config_elem)
            
            # Cache containers
            for elem in root.iter():
                eid = elem.get('id')
                if eid:
                    self._id_cache[name][eid] = self._parse_attributes(elem.attrib, name)
            
            print(f"Loaded layout: {name}")
            return True
        except Exception as e:
            print(f"Error loading layout {name}: {e}")
            return False

    def _parse_attributes(self, attribs: Dict[str, str], mode_name: str = None) -> Dict[str, Any]:
        """Parse and convert attribute values to appropriate types."""
        parsed = {}
        
        for key, value in attribs.items():
            if isinstance(value, str) and value.startswith("@"):
                var_name = value[1:]
                resolved = None
                
                # Check global style cache first
                if var_name in self._style_cache:
                    resolved = self._style_cache[var_name]
                else:
                    resolved = self._resolve_theme_variable(var_name)
                
                if resolved is not None:
                    parsed[key] = resolved
                else:
                    parsed[key] = self._parse_value(value)
            else:
                parsed[key] = self._parse_value(value)
        return parsed

    def _parse_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        if value is None:
            return None
        
        # Boolean values
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        if value.endswith('%'):
            return value
        
        return value

    def get_config(self) -> Dict[str, Any]:
        """Get the config for the current mode."""
        mode = self.current_mode_name
        if mode in self._config_cache:
            return self._config_cache[mode]
        
        # Fallback to default
        if "default" in self._config_cache:
            return self._config_cache["default"]
        
        sizes = self.theme_config.get("theme", {}).get("sizes", {})
        return {
            'widths': {
                'level_0': sizes.get('level_0_width', 200),
                'level_1': sizes.get('level_1_width', 260),
                'level_2': sizes.get('level_2_width', 260),
                'collapsed': sizes.get('collapsed_width', 60)
            },
            'animation': {'duration': self.theme_config.get("display", {}).get("animation_duration", 100)}
        }

    def get_behavior(self) -> Dict[str, Any]:
        """Get behavior config for current mode."""
        return self._behavior_cache.get(self.current_mode_name, {})

    def get_animation(self, name: str) -> Dict[str, Any]:
        """Get animation config by name."""
        if name in self._animation_cache:
            return self._animation_cache[name]
        return {
            'duration': self.get_animation_duration(),
            'easing': 'linear'
        }

    def get_widths(self) -> Dict[str, int]:
        """Get the width configuration for the current mode."""
        config = self.get_config()
        return config.get('widths', {
            'level_0': 200, 'level_1': 260, 'level_2': 260, 'collapsed': 60
        })

    def get_animation_duration(self) -> int:
        """Get the animation duration for the current mode."""
        config = self.get_config()
        return config.get('animation', {}).get('duration', 100)

    def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Find an element by ID in the current mode."""
        mode = self.current_mode_name
        
        # Check mode-specific cache
        if mode in self._id_cache and element_id in self._id_cache[mode]:
            return self._id_cache[mode][element_id]
        
        # Fallback to default mode
        if "default" in self._id_cache and element_id in self._id_cache["default"]:
            return self._id_cache["default"][element_id]
        
        return None

    def check_for_updates(self):
        """Check if main.xml has changed and reload."""
        path = os.path.join(self.layout_dir, "main.xml")
        
        if os.path.exists(path):
            try:
                current_mtime = os.path.getmtime(path)
                if current_mtime > self.file_timestamp:
                    print("Reloading main.xml")
                    self._load_main_layout()
            except OSError:
                pass

    def get_layout_structure(self) -> Dict[str, Any]:
        """Returns a simplified dictionary representation of the layout."""
        if self.main_layout is not None:
            return self._parse_element(self.main_layout)
        return {}

    def _parse_element(self, element) -> Dict[str, Any]:
        """Parse an XML element to dictionary."""
        data = {
            "tag": element.tag,
            "attrib": self._parse_attributes(element.attrib),
            "children": [self._parse_element(child) for child in element]
        }
        return data

    # ==========================================
    # Menu Access Methods
    # ==========================================
    
    def get_menus(self) -> Dict[str, Dict[str, Any]]:
        """Get all menu definitions."""
        return self._menu_cache
    
    def get_menus_list(self) -> List[Dict[str, Any]]:
        """Get menus as a list (compatible with old JSON format)."""
        return list(self._menu_cache.values())
    
    def get_menu(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific menu by name."""
        return self._menu_cache.get(name)
    
    def get_menu_item(self, menu_name: str, item_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific item from a menu."""
        menu = self._menu_cache.get(menu_name)
        if not menu:
            return None
        return self._find_item_recursive(menu.get('options', []), item_name)
    
    def _find_item_recursive(self, options: List[Dict], item_name: str) -> Optional[Dict[str, Any]]:
        """Recursively find an item by name in options."""
        for opt in options:
            if not isinstance(opt, dict):
                continue
            if opt.get('name') == item_name:
                return opt
            # Check nested options (groups)
            nested = opt.get('options')
            if isinstance(nested, list):
                found = self._find_item_recursive(nested, item_name)
                if found:
                    return found
        return None
    
    def set_menu_value(self, item_name: str, value: Any) -> bool:
        """Set a menu item's value by name (searches all menus)."""
        for menu in self._menu_cache.values():
            item = self._find_item_recursive(menu.get('options', []), item_name)
            if item:
                item['value'] = value
                return True
        return False
    
    def get_menu_value(self, item_name: str) -> Any:
        """Get a menu item's current value by name."""
        for menu in self._menu_cache.values():
            item = self._find_item_recursive(menu.get('options', []), item_name)
            if item:
                return item.get('value')
        return None

    # ==========================================
    # Style Access Methods
    # ==========================================
    
    def get_text_style(self, name: str) -> Dict[str, Any]:
        """Get a text style by name."""
        return self._text_style_cache.get(name, {})
    
    def get_border_style(self, name: str) -> Dict[str, Any]:
        """Get a border style by name."""
        return self._border_style_cache.get(name, {})
    
    def get_all_text_styles(self) -> Dict[str, Dict[str, Any]]:
        """Get all text styles."""
        return self._text_style_cache
    
    def get_all_border_styles(self) -> Dict[str, Dict[str, Any]]:
        """Get all border styles."""
        return self._border_style_cache

    # ==========================================
    # Stats Access Methods
    # ==========================================
    
    def get_stats_config(self) -> Dict[str, Any]:
        """Get stats configuration."""
        return self._stats_cache
    
    def get_quick_stats_for_mode(self, mode_name: str) -> List[str]:
        """Get quick stats list for a specific camera mode."""
        return self._stats_cache.get('modes', {}).get(mode_name, [])
    
    def get_available_stats(self) -> List[str]:
        """Get list of all available stats."""
        return self._stats_cache.get('available', [])

    # ==========================================
    # Global Config Access Methods
    # ==========================================
    
    def get_icon_aliases(self) -> Dict[str, str]:
        """Get icon aliases mapping."""
        return self._global_config.get('icon_aliases', {})
    
    def get_icon_name(self, setting_name: str) -> str:
        """Get the icon filename for a setting (applies aliases)."""
        aliases = self._global_config.get('icon_aliases', {})
        return aliases.get(setting_name, setting_name)
    
    def get_camera_modes(self) -> List[str]:
        """Get list of available camera modes."""
        return self._global_config.get('modes', ['auto', 'manual', 'timelapse'])
    
    def get_mode_colors(self) -> Dict[str, str]:
        """Get mode colors mapping."""
        return self._global_config.get('mode_colors', {})
    
    def get_mode_color(self, mode_name: str) -> str:
        """Get color for a specific camera mode."""
        colors = self._global_config.get('mode_colors', {})
        return colors.get(mode_name, '#FFFFFF')
    
    def get_named_animation_duration(self, animation_name: str) -> int:
        """Get animation duration in ms by animation name from style config."""
        anim = self._animation_cache.get(animation_name, {})
        # Fall back to theme config animation_duration if specific animation not found
        if not anim:
            return self.theme_config.get('display', {}).get('animation_duration', 100)
        return anim.get('duration', 100)
    
    def get_flash_duration(self) -> int:
        """Get flash effect duration in ms."""
        return self.get_named_animation_duration('flash')
    
    def get_icon_path(self) -> str:
        """Get the base path for icons."""
        return self._global_config.get('icons', {}).get('path', 'src/ui/icons')
    
    def get_icon_extension(self) -> str:
        """Get the icon file extension."""
        return self._global_config.get('icons', {}).get('extension', '.svg')
    
    def get_text_scroll_config(self) -> Dict[str, Any]:
        """Get text scroll configuration."""
        return self._global_config.get('text_scroll', {'speed': 0.05, 'pause_ms': 1000})
    
    def get_navigation_config(self) -> Dict[str, Any]:
        """Get navigation behavior configuration."""
        return self._global_config.get('navigation', {
            'wrap_menus': True,
            'wrap_items': True,
            'auto_collapse_delay': 0
        })
    
    def get_startup_config(self) -> Dict[str, Any]:
        """Get startup configuration (show_stats, show_menu)."""
        return self._global_config.get('startup', {
            'show_stats': True,
            'show_menu': False
        })
    
    def get_formatter(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value formatter by key name."""
        return self._formatters_cache.get(key)
    
    def get_all_formatters(self) -> Dict[str, Dict[str, Any]]:
        """Get all value formatters."""
        return self._formatters_cache
    
    def get_slot(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a slot definition by name."""
        return self._slots_cache.get(name)
    
    def get_all_slots(self) -> Dict[str, Dict[str, Any]]:
        """Get all slot definitions."""
        return self._slots_cache
    
    def get_overlay(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        """Get an overlay definition by ID."""
        return self._overlays_cache.get(overlay_id)
    
    def get_all_overlays(self) -> Dict[str, Dict[str, Any]]:
        """Get all overlay definitions."""
        return self._overlays_cache
    
    def format_value(self, key: str, value: Any) -> str:
        """Format a value using the configured formatter for that key."""
        formatter = self._formatters_cache.get(key)
        if not formatter:
            return str(value)
        
        fmt_type = formatter.get('type', 'string')
        
        if fmt_type == 'shutter_speed':
            if isinstance(value, (int, float)) and value > 0:
                if value >= 1000000:
                    return f"{value / 1000000:.1f}s"
                elif value >= 1000:
                    fraction = 1000000 / value
                    if fraction >= 1:
                        return f"1/{int(fraction)}"
                    return f"{value / 1000:.0f}ms"
                else:
                    return f"{value}µs"
            return str(value)
        
        elif fmt_type == 'resolution':
            sep = formatter.get('separator', '×')
            if isinstance(value, str) and ',' in value:
                parts = value.split(',')
                return f"{parts[0]}{sep}{parts[1]}"
            elif isinstance(value, tuple):
                return f"{value[0]}{sep}{value[1]}"
            return str(value)
        
        elif fmt_type == 'signed_number':
            if isinstance(value, (int, float)):
                sign = '+' if value > 0 else ''
                return f"{sign}{value}"
            return str(value)
        
        # Default: apply prefix/suffix
        prefix = formatter.get('prefix', '')
        suffix = formatter.get('suffix', '')
        return f"{prefix}{value}{suffix}"

    # ==========================================
    # Layout Access Methods
    # ==========================================
    
    def get_layout(self, name: str = None) -> Optional[Dict[str, Any]]:
        """Get a layout definition by name, or current layout if none specified."""
        if name is None:
            name = self.current_mode_name
        
        # First check layouts cache
        if name in self._layouts_cache:
            return self._layouts_cache[name]
        
        # Fallback to 'default' layout
        return self._layouts_cache.get('default')
    
    def get_layout_type(self, name: str = None) -> str:
        """Get the layout type (multi_column, single_panel, overlay, etc.)."""
        layout = self.get_layout(name)
        return layout.get('type', 'multi_column') if layout else 'multi_column'
    
    def get_column_config(self, column_id: str, mode_name: str = None) -> Dict[str, Any]:
        """Get the configuration for a specific column, with mode overrides applied."""
        if mode_name is None:
            mode_name = self.current_mode_name
        
        # Start with base layout column config
        layout = self.get_layout()
        base_config = {}
        
        if layout and column_id in layout.get('columns', {}):
            base_config = layout['columns'][column_id].copy()
        
        # Apply mode-specific overrides
        if mode_name in self._mode_overrides_cache:
            overrides = self._mode_overrides_cache[mode_name]
            if column_id in overrides.get('columns', {}):
                style_override = overrides['columns'][column_id]
                if 'style' in base_config:
                    base_config['style'].update(style_override)
                else:
                    base_config['style'] = style_override
        
        return base_config
    
    def get_column_style(self, column_id: str, mode_name: str = None) -> Dict[str, Any]:
        """Get the style for a specific column with mode overrides."""
        config = self.get_column_config(column_id, mode_name)
        return config.get('style', {})
    
    def get_column_collapsed_style(self, column_id: str) -> Dict[str, Any]:
        """Get the collapsed display style for a column."""
        layout = self.get_layout()
        if layout and column_id in layout.get('columns', {}):
            return layout['columns'][column_id].get('collapsed_style', {})
        return {}
    
    def get_mode_override(self, mode_name: str) -> Dict[str, Any]:
        """Get all overrides for a specific mode."""
        return self._mode_overrides_cache.get(mode_name, {})
    
    def should_collapse_column(self, column_id: str, current_level: int) -> bool:
        """Determine if a column should be collapsed based on current menu level."""
        layout = self.get_layout()
        if not layout or column_id not in layout.get('columns', {}):
            return False
        
        col_config = layout['columns'][column_id]
        collapse_when = col_config.get('collapse_when')
        
        if not collapse_when:
            return False
        
        if collapse_when == 'never':
            return False
        
        # Parse simple conditions like "level > 0"
        if collapse_when.startswith('level >'):
            try:
                threshold = int(collapse_when.split('>')[1].strip())
                return current_level > threshold
            except (ValueError, IndexError):
                return False
        
        return False
    
    def is_column_visible(self, column_id: str, current_level: int) -> bool:
        """Determine if a column should be visible based on current menu level."""
        layout = self.get_layout()
        if not layout or column_id not in layout.get('columns', {}):
            return True
        
        col_config = layout['columns'][column_id]
        visible_when = col_config.get('visible_when')
        
        if not visible_when:
            return True
        
        if visible_when == 'false':
            return False
        
        # Parse simple conditions like "level >= 1"
        if 'level >=' in visible_when:
            try:
                threshold = int(visible_when.split('>=')[1].strip())
                return current_level >= threshold
            except (ValueError, IndexError):
                return True
        elif 'level >' in visible_when:
            try:
                threshold = int(visible_when.split('>')[1].strip())
                return current_level > threshold
            except (ValueError, IndexError):
                return True
        
        return True
    
    def get_all_layouts(self) -> Dict[str, Dict[str, Any]]:
        """Get all layout definitions."""
        return self._layouts_cache
