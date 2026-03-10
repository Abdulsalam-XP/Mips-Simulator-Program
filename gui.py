import streamlit as st
import pandas as pd
from memory import MipsMemory
from datapath import MipsDatapath
from main import decode, get_type_instruction, get_machine_code, REG_FUNCT, REG_MAP

st.set_page_config(page_title="MIPS Simulation Program", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap');

:root {
  --bg:       #111113;
  --surface:  #18181b;
  --raised:   #1e1e22;
  --border:   #27272a;
  --border-hi:#3f3f46;
  --accent:   #6366f1;
  --accent-d: rgba(99,102,241,0.15);
  --green:    #22c55e;
  --green-d:  rgba(34,197,94,0.12);
  --red:      #ef4444;
  --amber:    #f59e0b;
  --text:     #fafafa;
  --text-mid: #71717a;
  --text-dim: #3f3f46;
}

html, body, [class*="css"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Geist', sans-serif !important;
}
.stApp { background: var(--bg) !important; }
header[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
footer { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Top bar ── */
.topbar {
  height: 48px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 10px;
}
.topbar-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.01em;
}
.topbar-sub {
  font-size: 11.5px;
  color: var(--text-dim);
  margin-left: 2px;
}
.topbar-badge {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--text-mid);
  font-family: 'Geist Mono', monospace;
}

/* ── Two-column shell ── */
.two-col {
  display: flex;
  height: calc(100vh - 48px);
}
.col-left {
  width: 380px;
  min-width: 300px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.col-right {
  flex: 1;
  background: var(--bg);
  overflow-y: auto;
  padding: 20px 24px;
}

/* ── Left panel sections ── */
.left-section {
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}
.left-section:last-child { border-bottom: none; flex: 1; }
.section-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 10px;
  font-family: 'Geist', sans-serif;
}

/* ── Stat row ── */
.stat-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.stat-box {
  flex: 1;
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
}
.stat-label {
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 4px;
}
.stat-value {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  font-family: 'Geist Mono', monospace;
}

/* ── Status pill ── */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 500;
}
.pill-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
}

/* ── Right panel output blocks ── */
.out-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 16px;
  overflow: hidden;
}
.out-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--raised);
}
.out-header-title {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-mid);
  letter-spacing: 0.04em;
  font-family: 'Geist', sans-serif;
}
.out-header-count {
  margin-left: auto;
  font-size: 10.5px;
  color: var(--text-dim);
  font-family: 'Geist Mono', monospace;
}
.out-body { padding: 14px 16px; }
.out-empty {
  padding: 18px 16px;
  font-size: 12px;
  color: var(--text-dim);
  font-family: 'Geist Mono', monospace;
}

/* ── Streamlit widgets ── */
textarea {
  background: var(--bg) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
  font-family: 'Geist Mono', monospace !important;
  font-size: 12.5px !important;
  line-height: 1.75 !important;
  resize: none !important;
}
textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
  outline: none !important;
}

.stButton > button {
  background: var(--raised) !important;
  border: 1px solid var(--border-hi) !important;
  color: var(--text-mid) !important;
  font-family: 'Geist', sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border-radius: 7px !important;
  padding: 5px 14px !important;
  width: 100% !important;
  transition: all 0.12s !important;
}
.stButton > button:hover {
  background: #27272a !important;
  border-color: #52525b !important;
  color: var(--text) !important;
}
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  background: #7577f3 !important;
  box-shadow: 0 4px 18px rgba(99,102,241,0.4) !important;
}
.stButton > button:disabled {
  opacity: 0.35 !important;
}

[data-testid="stDataFrame"] {
  background: var(--bg) !important;
  border: none !important;
  border-radius: 0 !important;
}
[data-testid="stDataFrame"] th {
  background: var(--raised) !important;
  color: var(--text-dim) !important;
  font-family: 'Geist', sans-serif !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border) !important;
  padding: 6px 12px !important;
}
[data-testid="stDataFrame"] td {
  color: var(--text) !important;
  font-family: 'Geist Mono', monospace !important;
  font-size: 12px !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 5px 12px !important;
}
[data-testid="stDataFrame"] tr:hover td {
  background: var(--raised) !important;
}

label { display: none !important; }
p { color: var(--text-mid) !important; font-size: 12px !important; }
h1,h2,h3 { color: var(--text) !important; font-family: 'Geist', sans-serif !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #52525b; }
</style>
""", unsafe_allow_html=True)

if "memory"           not in st.session_state: st.session_state.memory           = MipsMemory()
if "datapath"         not in st.session_state: st.session_state.datapath         = MipsDatapath(st.session_state.memory)
if "history"          not in st.session_state: st.session_state.history          = []
if "data_mem_history" not in st.session_state: st.session_state.data_mem_history = {}
if "is_loaded"        not in st.session_state: st.session_state.is_loaded        = False
if "cycle"            not in st.session_state: st.session_state.cycle            = 0

def load_code(assembly_text):
    st.session_state.memory           = MipsMemory()
    st.session_state.datapath         = MipsDatapath(st.session_state.memory)
    st.session_state.history          = []
    st.session_state.data_mem_history = {}
    st.session_state.is_loaded        = True
    st.session_state.cycle            = 0
    instructions = [l.strip() for l in assembly_text.split('\n') if l.strip()]
    loaded = 0
    for i, instr in enumerate(instructions):
        try:
            parts            = decode(instr)
            type_instruction = get_type_instruction(parts, REG_FUNCT, REG_MAP)
            machine_code     = get_machine_code(type_instruction)
            st.session_state.memory.load_initial_data(i * 4, machine_code)
            loaded += 1
        except Exception as e:
            st.session_state.history.append({
                "Cycle": "-", "PC": "-", "Instr": "-",
                "RegWr": "-", "MemWr": "-", "Note": f"ERR: {instr} → {e}"
            })
    return loaded

def do_step():
    mem = st.session_state.memory
    dp  = st.session_state.datapath
    if dp.pc not in mem.storage:
        return False
    current_pc  = dp.pc
    instruction = mem.read(dp.pc)
    opcode = (instruction >> 26) & 0x3F
    rs     = (instruction >> 21) & 0x1F
    rt     = (instruction >> 16) & 0x1F
    rd     = (instruction >> 11) & 0x1F
    shamt  = (instruction >> 6)  & 0x1F
    funct  =  instruction        & 0x3F
    imm    =  instruction        & 0xFFFF
    signals               = dp.control_unit(opcode)
    reg_data1, reg_data2  = dp.register_file(rs, rt, 0, 0, 0, 0)
    extended_imm          = dp.sign_extend(imm)
    write_reg             = dp.mux(rt, rd, signals["RegDst"])
    alu_in2               = dp.mux(reg_data2, extended_imm, signals['ALUSrc'])
    alu_ctrl              = dp.alu_control(signals["ALUOp"], funct)
    alu_result, zero_flag = dp.alu(reg_data1, alu_in2, alu_ctrl, shamt)
    mem_data = 0
    if signals["MemRead"]:  mem_data = mem.read(alu_result)
    if signals["MemWrite"]:
        mem.write(alu_result, reg_data2)
        st.session_state.data_mem_history[alu_result] = reg_data2
    final_write_data = dp.mux(alu_result, mem_data, signals["MemtoReg"])
    dp.register_file(rs, rt, write_reg, final_write_data, signals["RegWrite"])
    dp.pc += 4
    st.session_state.cycle += 1
    st.session_state.history.append({
        "Cycle": st.session_state.cycle,
        "PC":    hex(current_pc),
        "Instr": hex(instruction),
        "RegWr": signals["RegWrite"],
        "MemWr": signals["MemWrite"],
    })
    return True

loaded  = st.session_state.is_loaded
pc_val  = st.session_state.datapath.pc
cyc_val = st.session_state.cycle

st.markdown(f"""
<div class="topbar">
  <span class="topbar-title">MIPS Simulation Program</span>
  <span class="topbar-sub">· Single-Cycle Datapath</span>
  <div class="topbar-badge">
    <span style="color:#3f3f46;">·</span>
    <span>Cycle&nbsp;<b style="color:#fafafa;">{cyc_val}</b></span>
    <span style="color:#3f3f46;">·</span>
    <span style="color:{'#22c55e' if loaded else '#f59e0b'};">
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1.1, 2.6], gap="small")

with left_col:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    asm_input = st.text_area(
        "asm", height=260,
        placeholder="addi $t0, $zero, 5\nadd  $s0, $t0, $t1\nsw   $s0, 0($zero)\n...",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    loaded_count = None
    if st.button("Assemble & Load", type="primary", use_container_width=True):
        loaded_count = load_code(asm_input)

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        step_clicked = st.button("Step →", disabled=not loaded, use_container_width=True)
    with b2:
        run_clicked  = st.button("Run All", disabled=not loaded, use_container_width=True)

    if loaded_count is not None:
        st.markdown(
            f'<div style="margin-top:8px;display:flex;align-items:center;gap:6px;'
            f'background:var(--green-d);border:1px solid rgba(34,197,94,0.25);'
            f'border-radius:7px;padding:7px 10px;font-size:11.5px;color:#22c55e;'
            f'font-family:\'Geist Mono\',monospace;">'
            f'✓ &nbsp;{loaded_count} instruction(s) loaded</div>',
            unsafe_allow_html=True,
        )
    for r in [r for r in st.session_state.history if r.get("Cycle") == "-"]:
        st.markdown(
            f'<div style="margin-top:6px;background:rgba(239,68,68,0.08);'
            f'border:1px solid rgba(239,68,68,0.25);border-radius:7px;'
            f'padding:7px 10px;font-size:11px;color:#ef4444;'
            f'font-family:\'Geist Mono\',monospace;">{r["Note"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">State</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-box">
        <div class="stat-label">Program Counter</div>
        <div class="stat-value">0x{pc_val:04X}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Cycle</div>
        <div class="stat-value">{cyc_val}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

if step_clicked: do_step()
if run_clicked:
    while do_step(): pass

with right_col:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    trace_rows = [r for r in st.session_state.history if r.get("Cycle") != "-"]
    trace_count = len(trace_rows)

    reg_col, mem_col = st.columns(2, gap="medium")

    with reg_col:
        dp = st.session_state.datapath
        reg_rows = [{"Idx": i, "Name": dp.REG_NAME.get(i, f"R{i}"),
                     "Dec": dp.registers[i],
                     "Hex": f"0x{dp.registers[i] & 0xFFFFFFFF:08X}"}
                    for i in range(32)]
        st.markdown("""
        <div class="out-block">
          <div class="out-header">
            <span class="out-header-title">Register File</span>
            <span class="out-header-count">32 regs</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(reg_rows), use_container_width=True,
                     hide_index=True, height=420)

    with mem_col:
        st.markdown(f"""
        <div class="out-block">
          <div class="out-header">
            <span class="out-header-title">Data Memory</span>
            <span class="out-header-count">{len(st.session_state.data_mem_history)} writes</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.data_mem_history:
            dmem_rows = [{"Addr": hex(a), "Dec": v, "Hex": hex(v)}
                         for a, v in sorted(st.session_state.data_mem_history.items())]
            st.dataframe(pd.DataFrame(dmem_rows), use_container_width=True,
                         hide_index=True, height=420)
        else:
            st.markdown(
                '<div class="out-empty">— execute a sw instruction —</div>',
                unsafe_allow_html=True,
            )