import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from ui_lint import lint

def rules(code, name='UI.client.lua'): return {f['rule'] for f in lint(code, name)}

def test_emoji_in_log_fails():
    assert 'emoji.in_log' in rules('print("[InventoryUI] Ready \\u2705")'.replace('\\u2705', '\u2705'))
def test_ascii_log_ok():
    assert 'emoji.in_log' not in rules('print("[InventoryUI] Ready")')
def test_emoji_icon_warns():
    assert 'emoji.in_ui_text' in rules('label.Text = "\U0001FA99"')
def test_comment_emoji_ignored():
    assert not rules('-- \U0001FA99 coin\nlocal x = 1')
def test_repeated_asset_id_fails():
    code = '\n'.join(f'icon{i}.Image = "rbxassetid://7123456789"' for i in range(4))
    assert 'asset.repeated_id' in rules(code, 'AssetManifest.lua')
def test_suspicious_asset_id_fails():
    assert 'asset.suspicious_id' in rules('a.Image = "rbxassetid://1234567890"', 'AssetManifest.lua')
def test_single_real_looking_id_ok():
    assert not (rules('a.Image = "rbxassetid://7123456789"', 'AssetManifest.lua') & {'asset.repeated_id', 'asset.suspicious_id'})
def test_inline_asset_warns():
    assert 'asset.id_outside_manifest' in rules('a.Image = "rbxassetid://7123456789"', 'Inventory.client.lua')
def test_ignore_inset_warns():
    assert 'ui.topbar_overlap_risk' in rules('gui.IgnoreGuiInset = true')
def test_screen_insets_ok():
    assert 'ui.topbar_overlap_risk' not in rules('gui.IgnoreGuiInset = true\ngui.ScreenInsets = Enum.ScreenInsets.TopbarSafeInsets')
def test_large_panel_warns():
    assert 'ui.large_panel' in rules("local f = Instance.new('Frame')\nf.Size = UDim2.fromScale(0.9, 0.9)")
def test_constrained_panel_has_no_constraint_warning():
    assert 'ui.no_size_constraint' not in rules("local f = Instance.new('Frame')\nInstance.new('UISizeConstraint')")
def test_loading_never_hidden_warns():
    assert 'ui.loading_never_hidden' in rules('loadingLabel.Text = "Loading..."')
def test_loading_hidden_ok():
    assert 'ui.loading_never_hidden' not in rules('loadingLabel.Text = "Loading..."\nloadingLabel.Visible = false')
def test_unguarded_init_warns():
    assert 'lifecycle.unguarded_init' in rules('for _, service in services do\n  service:Init()\nend')
def test_guarded_init_ok():
    assert 'lifecycle.unguarded_init' not in rules('for _, service in services do\n  if service.Init then service:Init() end\nend')
def test_small_text_warns():
    assert 'ui.small_text' in rules('l.TextSize = 9')
