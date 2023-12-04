-- python.lua: python ftplugin
-- (see also python.vim)

-- Use treesitter highlight for python
-- Note: nvim >= 0.9 recommended, injection doesn't work well in 0.8.x
require("config.treesitter").setup_highlight('python')

-- Formatting
require("config.formatting").create_buf_command("Isort", "isort")

local bufnr = vim.api.nvim_get_current_buf()
vim.api.nvim_create_autocmd('LspAttach', {
  once = true,
  buffer = bufnr,
  callback = function()
    require("config.formatting").maybe_autostart_autoformatting(bufnr, function(project_root)
      local style_yapf = assert(project_root) .. '/.style.yapf'
      if vim.fn.filereadable(style_yapf) > 0 then
        return true, ("Detected %s"):format(style_yapf)
      end
      local pyproject_toml = assert(project_root) .. '/pyproject.toml'
      if vim.fn.filereadable(pyproject_toml) > 0 then
        local ok, match = require("utils.path_utils").file_contains_pattern(pyproject_toml,
            { "^%[tool%.yapf%]", "^%[tool%.isort%]"})
        if ok and match then
          return true, ("pyproject.toml:%s: %s"):format(match.line, match.match)
        end
      end
      return false
    end)
  end,
})

------------------------------------------------------------------------------
-- Keymaps (see $DOTVIM/lua/lib/python.lua)
------------------------------------------------------------------------------
local vim_cmd = function(x) return '<Cmd>' .. vim.trim(x) .. '<CR>' end
local bufmap = function(mode, lhs, rhs, opts)
  return vim.keymap.set(mode, lhs, rhs, vim.tbl_deep_extend("error", { buffer = true }, opts or {}))
end
local make_repeatable_keymap = require("utils.rc_utils").make_repeatable_keymap

-- Toggle breakpoint (a non-DAP way)
bufmap('n', '<leader>b', '<Plug>(python-toggle-breakpoint)', { remap = true })
vim.keymap.set('n', '<Plug>(python-toggle-breakpoint)', function()
  require("lib.python").toggle_breakpoint()
end, { buffer = false })

-- Toggle f-string
local toggle_fstring = vim_cmd [[ lua require("lib.python").toggle_fstring() ]]
bufmap('n', '<leader>tf', make_repeatable_keymap('n', '<Plug>(toggle-fstring-n)', toggle_fstring), { remap = true })
bufmap('i', '<C-f>', toggle_fstring)

-- Toggle line comments (e.g., `type: ignore`, `yapf: ignore`)
local function make_repeatable_toggle_comment_keymap(comment)
  local auto_lhs = ("<Plug>(ToggleLineComment-%s)"):format(comment:gsub('%W', ''))
  return make_repeatable_keymap('n', auto_lhs, function()
    require("lib.python").toggle_line_comment(comment)
  end)
end
bufmap('n', '<leader>ti', make_repeatable_toggle_comment_keymap("type: ignore"), { remap = true })
bufmap('n', '<leader>ty', make_repeatable_toggle_comment_keymap("yapf: ignore"), { remap = true })

