# Neovim like theme 

Neovim theme is a neovim like theme for zola.

![screenshot](./screenshot.png)

exemple: [https://super-botman.github.io](https://super-botman.github.io)

## Installation
```bash
cd themes
git clone https://github.com/Super-Botman/neovim-theme.git
mv neovim-theme/content/readme.md ../content
```

then enable it in your config

```toml
theme = "neovim-theme"
```

## Configuration

```toml
[extra]
# set the name of the blog
blog_name = "name"

# set the background image u want
background-image = "assets/background.jpg"

# this parameter allow you to configure specific init functions/shortcuts and commands
# the value has to be the path of you're config.js file
config_js = "config.js"

# allow you to include custom css into u're blog
custom_css = "style.css"
```

```js
const keys = {
  // "normal" keys are just keys typed on the page
  // for exemple " " is when space is typed
  normal: {
    " ": (event, element) => {
      alert("u pressed space key");
    },
  },

  // this is for keys when shift is pressed
  shortcut: {},
};

const commands = {
  // the key is used to specify the name of the command
  test: (command) => {
    alert("you entered 'test' command");

    // and then the return value with type and message
    return {
      type: "success", // "success" = green text, "error" = red text
      message: "command executed", // the text to show in the command line
    };
  },
};

function custom_init() {
  // here some code
}
```
