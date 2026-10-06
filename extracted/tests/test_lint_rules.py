import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lint_rules import lint

CASES = [
 ('bad_wait', "wait(1)", 'deprecated.wait', True),
 ('ok_task_wait', "task.wait(1)", 'deprecated.wait', False),
 ('bad_inst_new', "local p = Instance.new('Part', workspace)", 'style.instance_new_parent', True),
 ('ok_inst_new', "local p = Instance.new('Part')\np.Parent = workspace", 'style.instance_new_parent', False),
 ('bad_velocity', "part.Velocity = Vector3.new(0,10,0)", 'deprecated.velocity', True),
 ('ok_self_velocity', "self.Velocity = self.Velocity + v", 'deprecated.velocity', False),
 ('bad_stub_named', "local function f()\n    -- play effect here\nend", 'stub.empty_function', True),
 ('bad_stub_anon', "x = function(a) end", 'stub.empty_function', True),
 ('ok_commented_example', "-- local x = bus:Subscribe('a', function() end)", 'stub.empty_function', False),
 ('bad_zero_id', "a.AnimationId = 'rbxassetid://0'", 'asset.zero_id', True),
 ('ok_marked_id', "a.AnimationId = 'rbxassetid://REPLACE_WITH_ANIMATION_ID'", 'asset.zero_id', False),
 ('bad_client_damage', "local UIS = game:GetService('UserInputService')\nhumanoid:TakeDamage(10)", 'authority.client_damage', True),
 ('ok_server_damage', "local r = game.ReplicatedStorage.R\nr.OnServerEvent:Connect(function(p) h:TakeDamage(5) end)", 'authority.client_damage', False),
 ('bad_render_server', "remote.OnServerEvent:Connect(function() end)\nRunService.RenderStepped:Connect(f)", 'context.render_on_server', True),
 ('ok_render_client', "local UIS = game:GetService('UserInputService')\nRunService.RenderStepped:Connect(f)", 'context.render_on_server', False),
]
failed = []
for name, code, rule, expect in CASES:
    got = any(f['rule'] == rule for f in lint(code))
    if got != expect:
        failed.append(name)
print(f'{len(CASES) - len(failed)}/{len(CASES)} lint tests passed')
if failed:
    print('FAILED:', failed); sys.exit(1)
