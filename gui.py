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
.block-container { padding: 0 48px 48px 48px !important; max-width: 100% !important; }
            
.topbar {
  height: 90px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 48px;
  gap: 10px;
}
.topbar-title {
  font-size: 40.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.01em;
}

.left-section {
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}
.left-section:last-child { border-bottom: none; flex: 1; }
.section-label {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 10px;
  font-family: 'Geist', sans-serif;
}

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
  background: #2d2d44;
  color: white;
  font-weight: 600;
  border: 1px solid rgba(255,255,255,0.2);
}
          # Step button hover effect (only when enabled)
.stButton > button[kind="primary"]:hover {
  background: #38385a;
}        
          # Disabled button hover cursor effect 
.stButton > button:disabled {
  opacity: 0.05 !important;
}

</style>
""", unsafe_allow_html=True)

if "memory"           not in st.session_state: st.session_state.memory           = MipsMemory()
if "datapath"         not in st.session_state: st.session_state.datapath         = MipsDatapath(st.session_state.memory)
if "history"          not in st.session_state: st.session_state.history          = []
if "data_mem_history" not in st.session_state: st.session_state.data_mem_history = {}
if "is_loaded"        not in st.session_state: st.session_state.is_loaded        = False
if "cycle"            not in st.session_state: st.session_state.cycle            = 0
if "start_address" not in st.session_state: st.session_state.start_address = 0
if "wire_values" not in st.session_state: st.session_state.wire_values = {}

def load_code(assembly_text, start_address):
    st.session_state.memory           = MipsMemory()
    st.session_state.datapath         = MipsDatapath(st.session_state.memory)
    st.session_state.history          = []
    st.session_state.data_mem_history = {}
    st.session_state.is_loaded        = True
    st.session_state.cycle            = 0
    st.session_state.datapath.pc = start_address
    instructions = [l.strip() for l in assembly_text.split('\n') if l.strip()]
    loaded = 0
    for i, instr in enumerate(instructions):
        try:
            parts            = decode(instr)
            type_instruction = get_type_instruction(parts, REG_FUNCT, REG_MAP)
            machine_code     = get_machine_code(type_instruction)
            st.session_state.memory.load_initial_data(start_address + i * 4, machine_code)
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
    target =  instruction        & 0x3FFFFFF
    signals               = dp.control_unit(opcode)
    reg_data1, reg_data2  = dp.register_file(rs, rt, 0, 0, 0, 0)
    extended_imm          = dp.sign_extend(imm)

    next_pc = dp.pc + 4
    st.session_state.cycle += 1

    # ── J / JAL ──────────────────────────────────────────────────────────
    if signals["Jump"]:
        jump_target = (next_pc & 0xF0000000) | (target << 2)
        if signals["JAL"]:
            dp.register_file(rs, rt, 31, next_pc, 1)
        dp.pc = jump_target
        st.session_state.wire_values = {
            "PC":           hex(current_pc),
            "Instruction":  hex(instruction),
            "Opcode":       hex(opcode),
            "RS":           rs,
            "RT":           rt,
            "RD":           rd,
            "Shamt":        shamt,
            "Funct":        hex(funct),
            "IMM":          imm,
            "Target":       hex(target),
            "Extended IMM": extended_imm,
            "ALU Ctrl":     "N/A",
            "ALU Result":   "N/A",
            "Zero Flag":    "N/A",
            "RegWrite":     signals["RegWrite"],
            "MemRead":      signals["MemRead"],
            "MemWrite":     signals["MemWrite"],
            "ALUSrc":       signals["ALUSrc"],
            "MemtoReg":     signals["MemtoReg"],
            "RegDst":       signals["RegDst"],
            "Jump":         signals["Jump"],
            "JAL":          signals["JAL"],
            "Branch":       signals["Branch"],
        }
        st.session_state.history.append({
            "Cycle": st.session_state.cycle,
            "PC":    hex(current_pc),
            "Instr": hex(instruction),
            "RegWr": signals["RegWrite"],
            "MemWr": signals["MemWrite"],
        })
        return True

    # ── Normal pipeline ───────────────────────────────────────────────────
    write_reg             = dp.mux(rt, rd, signals["RegDst"])
    alu_in2               = dp.mux(reg_data2, extended_imm, signals['ALUSrc'])
    alu_ctrl              = dp.alu_control(signals["ALUOp"], funct)
    alu_result, zero_flag = dp.alu(reg_data1, alu_in2, alu_ctrl, shamt)

    st.session_state.wire_values = {
        "PC":           hex(current_pc),
        "Instruction":  hex(instruction),
        "Opcode":       hex(opcode),
        "RS":           rs,
        "RT":           rt,
        "RD":           rd,
        "Shamt":        shamt,
        "Funct":        hex(funct),
        "IMM":          imm,
        "Target":       hex(target),
        "Extended IMM": extended_imm,
        "ALU Ctrl":     alu_ctrl,
        "ALU Result":   alu_result,
        "Zero Flag":    zero_flag,
        "RegWrite":     signals["RegWrite"],
        "MemRead":      signals["MemRead"],
        "MemWrite":     signals["MemWrite"],
        "ALUSrc":       signals["ALUSrc"],
        "MemtoReg":     signals["MemtoReg"],
        "RegDst":       signals["RegDst"],
        "Jump":         signals["Jump"],
        "JAL":          signals["JAL"],
        "Branch":       signals["Branch"],
    }

    # ── JR ───────────────────────────────────────────────────────────────
    if alu_ctrl == "jr":
        dp.pc = reg_data1
        st.session_state.history.append({
            "Cycle": st.session_state.cycle,
            "PC":    hex(current_pc),
            "Instr": hex(instruction),
            "RegWr": 0,
            "MemWr": 0,
        })
        return True

    mem_data = 0
    if signals["MemRead"]:  mem_data = mem.read(alu_result)
    if signals["MemWrite"]:
        mem.write(alu_result, reg_data2)
        st.session_state.data_mem_history[alu_result] = reg_data2
    final_write_data = dp.mux(alu_result, mem_data, signals["MemtoReg"])
    dp.register_file(rs, rt, write_reg, final_write_data, signals["RegWrite"])
    dp.pc = next_pc
    st.session_state.history.append({
        "Cycle": st.session_state.cycle,
        "PC":    hex(current_pc),
        "Instr": hex(instruction),
        "RegWr": signals["RegWrite"],
        "MemWr": signals["MemWrite"],
    })
    return True

st.markdown(f"""
<div class="topbar">
  <span class="topbar-title">MIPS Simulation Program</span>
</div>
""", unsafe_allow_html=True)

loaded  = st.session_state.is_loaded
pc_val  = st.session_state.datapath.pc
cyc_val = st.session_state.cycle

left_column, right_column = st.columns([1.1, 2.6], gap="small")

with left_column:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    start_address = st.number_input(
      "Starting Address (hex offset)", 
      min_value=0, step=4, value=0,
      label_visibility="visible"
  )
    st.session_state.start_address = start_address

    asm_input = st.text_area(
        "asm", height=260,
        placeholder="addi $t0, $zero, 5\nadd  $s0, $t0, $t1\nsw   $s0, 0($zero)\n...",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.button("Assemble & Load", type="primary", use_container_width=True):
      load_code(asm_input, st.session_state.start_address)
      st.rerun()

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    _, middle_button, _ = st.columns([1, 2, 1])
with middle_button:
    if st.button("Step →", disabled=not st.session_state.is_loaded, use_container_width=True):
        do_step()
        st.rerun()

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

with right_column:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    trace_rows = [r for r in st.session_state.history if r.get("Cycle") != "-"]
    trace_count = len(trace_rows)

    reg_column, mem_column = st.columns(2, gap="medium")

    with reg_column:
        dp = st.session_state.datapath
        reg_rows = [{"Index": i, "Register": dp.REG_NAME.get(i, f"R{i}"),
                     "Value": dp.registers[i],
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

    with mem_column:
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
                '<div class="out-empty">— Load an SW instruction to see it appear here! —</div>',
                unsafe_allow_html=True,
            )
    if st.session_state.wire_values:
      st.markdown("""
      <div class="out-block">
        <div class="out-header">
          <span class="out-header-title">Datapath Wire Values</span>
          <span class="out-header-count">Last Cycle that is Executed</span>
        </div>
      </div>
      """, unsafe_allow_html=True)
      wire_rows = [{"Wire": k, "Value": v} 
                   for k, v in st.session_state.wire_values.items()]
      st.dataframe(pd.DataFrame(wire_rows), use_container_width=True, hide_index=True)