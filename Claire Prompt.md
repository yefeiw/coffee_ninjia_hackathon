你是一个资深全栈工程师 + 产品型设计师。请为一个名为 Coffee Ninja 的产品做一个可运行的单页 demo，核心目标是演示这条链路：

onboarding → match → “wow this is relevant” → willing to talk

这是一个职业发展社群里的 matching 产品。重点不是完整系统，而是一个能在 1–2 分钟内让人看懂价值的 demo。

====================
产品目标
====================
用户进入后，完成 onboarding，系统立即展示 1–2 个高质量 match（可以是 fake data），每个 match 都要有：
1. clear why-match explanation
2. 个性化 prompt
3. Interested action

用户在看到 match 时要明显感受到：
- 为什么是这个人
- 我能从他/她这里学到什么
- 我为什么值得点 Interested

====================
必须实现的页面与流程
====================

1) Onboarding（真实交互）
- 做成一个简洁、现代、移动端友好的 onboarding flow
- 用户需要填写/选择以下信息：

A. I can help with（供给）
要求：具体、可交易、不要抽象
示例：
- 从 consulting 转 product
- 如何进 Stripe / Notion
- 从 IC 到 manager transition

B. I want help with（需求）
示例：
- 想进入 AI PM
- 如何做 career pivot
- 如何提升 interview 表现

C. Experience signals（可信度）
轻量即可，不要复制 LinkedIn
- 公司
- 职级
- years

D. Conversation style（可选）
- tactical
- strategic
- casual

- 输入方式优先用 chips / selectable tags / short form
- 不要长文本，不要复杂表单
- Onboarding 完成后，要立刻给用户一个“你已经可以被匹配了”的反馈

2) Matching
- 展示 1–2 个高质量 match
- 可以全部用 mock data，但必须看起来非常合理
- 每个 match 卡片必须包含：

a. Name / headline
b. Why this match
   用非常直观的结构展示：
   - You want → They did
   - They want → You have

c. Conversation prompt
   要具体，不要泛泛而谈
   例如：
   - Ask: what was hardest in the transition?
   - Ask: how did you evaluate moving from consulting to PM?

d. Interested action
   - 一个明显的按钮
   - 点了之后显示一个 warm intro / next step 的状态
   - 不需要真实发消息，但要让用户感受到“已经准备好谈了”

====================
Match 类型要求
====================
请同时支持并展示以下三种 match 类型，至少 demo 里要出现其中 2 种，最好 3 种都出现：

1. Give-first match
- A 能帮 B，但 B 不能明显帮 A
- 用于 mentor 型用户

2. Mutual exchange
- 双向都有价值
- 这是最优且最重要的 match 类型

3. Peer match
- 同 level + 相似目标
- 更像同行交流，而不是上下游请教

每个 match 要标注它属于哪一种类型。

====================
用户体验要求
====================
- 整体风格：简洁、克制、可信、高质量
- 重点是“relevant”，不是“feature-rich”
- 不要做成社交 feed
- 不要做成复杂 CRM
- 不要做成完整聊天系统
- 不要做 scheduling
- 不要做真正的推荐算法后端
- 不要做登录/注册流程
- 不要做数据库持久化
- 所有数据都可以先放在前端 mock state 里

====================
Onboarding 的产品逻辑
====================
Onboarding 不只是收集信息，而是为了让系统能做出高质量 match。

请把 onboarding 做得像一个“结构化价值交换表单”，而不是 LinkedIn profile：
- 供给和需求都必须被结构化
- Experience signals 只保留最少必要信息
- Conversation style 是加分项，不是主流程

Onboarding 完成后，立刻显示类似：
- “We found 2 people who seem highly relevant”
- “You can help others too”
- “Your profile is now matchable”

====================
Matching 的产品逻辑
====================
每个 match 的核心信息结构必须清晰：

You want:
- xxx

They did:
- xxx

They want:
- xxx

You have:
- xxx

再加上：
- Why this matters
- What to ask
- Interested

这里的目标不是展示人物简介，而是让用户理解：
“这个人值得我花 30 分钟聊。”

====================
数据要求
====================
请先自己设计一组合理的 mock users / matches，至少包括：
- 1 个从 consulting 转 product / AI PM 的人
- 1 个想学 growth / strategy 的人
- 1 个 peer 类型的同级别用户
- 1 个 give-first 类型的 mentor-like 用户

这些 mock profiles 必须看起来像真实社区里的成员，而不是泛泛模板。

====================
实现要求
====================
请优先生成一个可运行的前端 demo。

建议：
- 单页应用
- 清晰的状态流转
- 适当的动画/过渡
- 卡片式信息展示
- 视觉层次明确

如果你要做交互，优先保证：
- onboarding 一步步推进
- 完成后自动进入 match 页
- match 页逐个展示
- 点击 Interested 后显示正反馈

====================
验收标准
====================
这个 demo 完成后，应该满足：
1. 任何人 30 秒内能看懂产品在解决什么问题
2. onboarding 能让用户愿意填写
3. match 页面能让用户立刻理解为什么 relevant
4. 用户会觉得“这个人值得聊”
5. 整个 demo 不依赖后端也能完整讲故事

====================
输出要求
====================
请直接生成代码，并确保可以本地运行。
如果需要，请先搭好项目结构，然后实现页面、组件、mock data 和状态流转。
重点是产品体验，不是算法复杂度。


chat的prompt

你是一个资深全栈工程师 + 产品型设计师。请在现有 Coffee Ninja demo 上新增一个 chat 功能，目标是把 matching 之后的“表达兴趣”真正闭环成一次可沟通的对话。

核心用户流程：
onboarding → match → Interested → warm intro appears in chat → 被 match 的人回复 → 协商 availability → 确认线上/线下 → 如果线下，确定见面地点

这是一个产品 demo，不是完整 production system。请优先保证体验完整、交互清晰、状态流转自然。

====================
产品目标
====================
当用户点击某个 match 的 Interested 后：
1. 系统自动在 chat 里发出 warm intro message
2. 被 match 的人可以回复
3. 双方可以在 chat 里协商可用时间（availability）
4. 双方可以选择线上或线下
5. 如果选择线下，继续在 chat 里确定见面地点
6. 最终形成一个“约好了”的状态

重点不是复杂 IM，而是让用户感受到：
“点了 Interested 之后，这件事真的开始推进了。”

====================
必须实现的 chat 体验
====================

1) Warm intro 自动进入 chat
- 用户在 match 卡片里点击 Interested 后，自动打开 chat panel / chat page
- 系统自动发一条 warm intro message
- 消息内容要自然、简洁、像真实引荐，而不是模板化机械文案

示例结构：
- 介绍双方是谁
- 为什么这次 connect relevant
- 提醒对方可以直接回复沟通时间

2) 对方可回复
- chat 里至少有两个参与者：
  - current user
  - matched person
- 被 match 的人可以回复消息
- 回复内容可以用 mock AI / preset responses / simple state machine 实现
- 不需要真实后端，但交互要像真的

3) 协商 availability
- chat 中要支持双方表达时间偏好
- 可以用快捷按钮、chips、quick replies 或简单 message actions
- 例如：
  - This week
  - Next week
  - Mornings
  - Evenings
  - 30 mins
  - 45 mins
  - 1 hour

- 需要让双方最终能达成一个可见的 availability agreement

4) 线上 / 线下选择
- 在 chat 中支持选择：
  - Online
  - In person
- 这个选择必须影响后续 UI state
- 如果选择 online：
  - 可以显示“Google Meet / Zoom / Zoom-like link will be shared”之类的占位状态
- 如果选择 in person：
  - 进入地点确认流程

5) 线下地点确认
- 如果选择线下，chat 里必须继续推进到 venue selection
- 可用方式：
  - 双方各提议地点
  - 系统推荐附近咖啡店
  - 最终确认一个地点
- 最终状态要显示：
  - confirmed time
  - confirmed place
  - confirmed mode = in person

====================
产品与交互要求
====================
- 这个 chat 不要做成通用 IM
- 不要做成 Slack 仿制品
- 不要做成复杂消息系统
- 不要做真实推送通知
- 不要做登录/注册
- 不要做数据库持久化
- 所有状态都可以存在前端 mock state 中

请把 chat 设计成一个“purpose-built intro-to-meeting workflow”，而不是 generic messaging。

====================
UI / 结构建议
====================
请做成以下之一：
- 右侧 chat drawer
- 独立 chat page
- match card 点击后展开 chat view

建议优先：
- 上半部分显示 match summary
- 下半部分显示 chat timeline
- 底部显示 quick reply buttons / action chips

====================
Chat 的状态机
====================
请实现一个简单但完整的状态机，至少包含这些状态：

1. idle
2. interest_expressed
3. warm_intro_sent
4. reply_received
5. availability_discussed
6. mode_selected
7. venue_discussed
8. confirmed

每个状态切换都要在 UI 里有明显反馈。

====================
消息内容要求
====================
消息必须自然、简洁、有真实感。

请生成以下类型的消息：
- warm intro message
- reply message from matched person
- availability reply
- online/offline preference
- venue proposal
- final confirmation message

消息风格要像真实职业社群里的引荐，而不是机器人客服。

====================
场景分支要求
====================
请支持至少两个完整分支：

分支 A：线上
- Interested
- warm intro
- reply
- availability alignment
- online selected
- confirm call / chat time

分支 B：线下
- Interested
- warm intro
- reply
- availability alignment
- in person selected
- venue discussed
- final venue confirmed

如果时间不够，优先把线下分支做完整，因为它比线上更能体现产品价值。

====================
和 match 的联动
====================
当用户在 match 卡片点 Interested 后：
- 自动进入对应 chat
- chat 顶部要保留 match 的核心信息
- 例如：
  - why this match
  - shared context
  - match type
- 用户不用离开当前 flow，就能继续沟通

====================
数据与 mock profiles
====================
请继续使用真实感强的 mock data，保持和已有 onboarding / matching 逻辑一致。

至少包括：
- 一个从 consulting 转 product / AI PM 的人
- 一个想学 growth / strategy 的人
- 一个 peer 类型的人
- 一个 mentor-like / give-first 类型的人

不同 match 的 chat 内容应该略有差异，体现不同 match type 的沟通方式。

====================
交互细节
====================
- 支持发送自定义文本
- 支持 quick replies
- 支持一键提议时间
- 支持一键选择 online / in person
- 支持在线下场景中提议地点
- 支持消息气泡、时间戳、发送状态
- 最终 confirmed 状态要明显可见

请尽量让 demo 看起来“像真的已经能用”，而不是像一个静态 prototype。

====================
实现优先级
====================
1. 先实现完整状态流转
2. 再补 chat UI
3. 再补 quick replies
4. 再补线上/线下分支
5. 再补线下地点确认

如果需要取舍：
- 优先保证流程完整
- 不要把精力花在花哨样式上
- 但要保持简洁、可信、现代

====================
验收标准
====================
这个 chat 功能完成后，必须满足：

1. 用户点击 Interested 后，能马上看到 warm intro 进入 chat
2. 被 match 的人可以回复
3. 双方可以协商时间
4. 可以选择 online 或 in person
5. 如果是 in person，可以最终确定地点
6. 最终能达到 confirmed 状态
7. 整个体验能无后端运行

====================
输出要求
====================
请直接修改现有 demo 代码，加入 chat 功能。
如果需要，你可以先搭建新的组件和 mock state，再接到现有 matching flow 上。
重点是把“表达兴趣之后，事情真的开始推进”这件事做出来。