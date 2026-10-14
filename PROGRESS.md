# GPT 娘 3D 桌宠

## V2 — Blender MCP（2026-10-14）

按用户要求停止 computer-use，安装并验证 MCP for Blender 2.1.9；Codex 全局 MCP 配置已注册 blender。Blender 插件偏好已保存，监听仅 127.0.0.1:9876，遥测关闭。

本次通过真正的 MCP stdio 协议调用实时 Blender 场景，未在 Blender 外直接改写 GLB。
已恢复先前 UI 工作的自动保存副本，使用用户新提供的 Meshy_AI_Aqua_Seraphina_1014082804_texture.glb。
完整高模 7,788,440 面，桌宠版 350,479 面；骨架从 20 根扩展为 35 根。
8 个动作重新编排，加入预备、保持、回弹、发梢/袖口/裙摆跟随；修正手指与裙片混合权重，采用基于网格邻接及空间接缝的平滑蒙皮。

新工程：blender/GPT-Girl-Desktop-Pet-V2.blend。
新桌宠模型：assets/gpt-girl-animated-v2.glb，app/main.cjs 已切换加载它。
原版工程和动画 GLB 保留。
验证：verification/mcp-export-result.json、verification/report.json 和各动作截图。
最终实际渲染器验证通过：8/8 动作、35 根骨骼、350479 三角面、透明背景正常；逐段采样的蒙皮坐标均有限。Blender 中 8 个动作首尾骨骼姿势误差均为 0。
完整高模和实时模型均无未绑定顶点。完整高模关闭视口计算，避免导出逐帧评估时变慢。
已启动 V2 桌宠；verification/live-state.json 确认 ready=true、visible=true、alwaysOnTop=true、无加载错误。
Blender 新窗口正在预览 Wave。插件持久启用确认见 verification/mcp-persistent-install.json（addon_status=[true,true]）。
仍无独立眼皮口型、无布料物理模拟，Walk 为原地踏步。

## V1 历史

已完成 Meshy 贴图与重拓扑；用户下载 GLB 至 assets。
Blender 已制作 20 根骨骼、平滑蒙皮及 8 个动作，保存可编辑工程与动画 GLB。
Electron + Three.js 透明置顶桌宠已通过实际渲染器验证，8 个动画均成功加载、骨骼变换有效，101518 个三角面，透明背景正常。

产物与操作详见使用说明.txt。
验证结果：verification/report.json，逐动作截图位于同目录。

已知限制：连体长裙和长发采用保守骨骼变形；没有闭眼口型或布料模拟；Walk 为原地踏步；桌宠不读取 Codex 工作状态。

桌面启动与置顶已确认（verification/live-state.json）。用户已实机确认：能看到桌宠，左键拖动和右键菜单均正常。桌面交互验收完成。
