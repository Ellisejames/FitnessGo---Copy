#!/usr/bin/env python3
"""
Responsive refactoring of fitnessv2.kv
Converts floating pos_hint center_y layouts → MDScrollView > MDBoxLayout flow
"""

import re

KV_PATH = '/home/runner/work/FitnessGo---Copy/FitnessGo---Copy/fitnessv2.kv'

with open(KV_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)


def replace_block(content, start_marker, end_marker, new_block):
    """Replace content from start_marker up to (not including) end_marker."""
    pattern = re.compile(
        re.escape(start_marker) + r'.*?(?=' + re.escape(end_marker) + r')',
        re.DOTALL
    )
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + new_block + content[m.end():]
        print(f"  ✅ Replaced: {start_marker[:40]}")
    else:
        print(f"  ❌ NOT FOUND: {start_marker[:60]}")
    return content


# =============================================================================
# 1. ButtonScreen
# =============================================================================
NEW_BUTTON_SCREEN = '''\
<ButtonScreen>:
    name: "button_screen"
    id: button_screen
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(20)
            size_hint_y: None
            height: self.minimum_height

            Image:
                source: "logo.png"
                size_hint: None, None
                width: "150dp"
                height: "150dp"
                pos_hint: {"center_x": 0.5}

            MDLabel:
                text: "Your Fitness Journey Starts Here.\\n"
                font_style: "Headline"
                role: "large"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDLabel:
                text: "Log in as:"
                font_style: "Title"
                role: "large"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDButton:
                id: new_btn
                style: "elevated"
                theme_width: "Custom"
                height: "50dp"
                size_hint_x: .5
                pos_hint: {"center_x": .5}
                on_release:
                    root.manager.transition.direction = "fade"
                    app.root.current = "login_screen"

                MDButtonText:
                    id: new_text
                    text: "Student"
                    pos_hint: {"center_x": .5, "center_y": .5}

            MDButton:
                id: create_btn
                style: "elevated"
                theme_width: "Custom"
                height: "50dp"
                size_hint_x: .5
                pos_hint: {"center_x": .5}
                on_release:
                    root.manager.transition.direction = "fade"
                    app.root.current = "admin_login_screen"

                MDButtonText:
                    id: create_text
                    text: "Admin"
                    pos_hint: {"center_x": .5, "center_y": .5}

'''

content = replace_block(content, '<ButtonScreen>:', '<loginScreen>:', NEW_BUTTON_SCREEN)

# =============================================================================
# 2. loginScreen
# =============================================================================
NEW_LOGIN_SCREEN = '''\
<loginScreen>:
    name: "login_screen"
    id: login_screen
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            Image:
                source: "logo.png"
                size_hint: None, None
                width: "150dp"
                height: "150dp"
                pos_hint: {"center_x": 0.5}

            MDLabel:
                text: "Fitness Go"
                font_style: "Display"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDLabel:
                text: "Username: "
                font_style: "Title"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDTextField:
                id: username_field
                mode: "outlined"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                radius: [30, 30, 30, 30]
                md_bg_color: 0.98, 1, 0.98, 1
                line_color_normal: 0, 0, 0, 0
                line_color_focus: 0, 0, 0, 0
                text_color_normal: 0, 0, 0, 1
                text_color_focus: 0, 0, 0, 1

                # ✅ canvas.after MUST come before child widgets
                canvas.after:
                    Color:
                        rgba: 0, 0.8, 0, 1
                    Line:
                        width: 2.5
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDTextFieldTrailingIcon:
                    icon: "account"
                    theme_icon_color: "Custom"
                    icon_color_normal: 0, 0.8, 0, 1   # green when unfocused
                    icon_color_focus: 0, 0.8, 0, 1

            MDLabel:
                text: "Password: "
                font_style: "Title"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(56)
                spacing: dp(4)

                MDTextField:
                    id: password_field
                    mode: "outlined"
                    size_hint_x: 1
                    password_mask: "\\u2022"
                    radius: [30, 30, 30, 30]
                    password: True
                    md_bg_color: 0.98, 1, 0.98, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0, 0, 0, 0
                    text_color_normal: 0, 0, 0, 1
                    text_color_focus: 0, 0, 0, 1

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDIconButton:
                    id: login_eye_icon
                    icon: "eye-off"
                    size_hint: None, None
                    size: "32dp", "32dp"
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0.639, 0, 1
                    on_release:
                        root.toggle_password_visibility(password_field, self)

            MDButton:
                style: "text"
                theme_text_color: "Custom"
                text_color: 0, 0.6, 0, 1
                halign: "left"
                valign: "middle"
                text_size: self.size
                on_release: root.open_forgot_password_dialog()

                MDButtonText:
                    text: "Forgot Password"

            MDButton:
                id: login_button
                style: "filled"
                pos_hint: {"center_x": 0.5}
                on_release:
                    root.manager.transition.direction = "fade"
                    root.login_user()

                MDButtonText:
                    text: "Log In"

            MDButton:
                style: "outlined"
                pos_hint: {"center_x": 0.5}
                on_release:
                    root.manager.transition.direction = "fade"
                    root.open_signup()

                MDButtonText:
                    text: "Create New Account"

'''

content = replace_block(content, '<loginScreen>:', '<SignupTermsScreen>:', NEW_LOGIN_SCREEN)

# =============================================================================
# 3. signupScreen
# =============================================================================
NEW_SIGNUP_SCREEN = '''\
<signupScreen>:
    name: "signup_screen"
    id: signup_screen
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "Tell us more about yourself"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                text: "To give you better experience and result"
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                text: "Full Name: "
                font_style: "Title"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDTextField:
                id: fullname_field
                mode: "outlined"                   # valid mode
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                radius: [30, 30, 30, 30]
                md_bg_color: 0.98, 1, 0.98, 1      # light background
                line_color_normal: 0, 0, 0, 0      # hide KivyMD\'s own outline
                line_color_focus: 0, 0, 0, 0
                text_color_normal: 0, 0, 0, 1
                text_color_focus: 0, 0, 0, 1

                canvas.after:
                    Color:
                        rgba: 0, 0.8, 0, 1         # green border
                    Line:
                        width: 2.5
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(90)
                spacing: dp(10)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(4)

                    MDLabel:
                        text: "Age: "
                        font_style: "Title"
                        role: "small"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(5)

                    MDTextField:
                        id: age_field
                        mode: "outlined"
                        size_hint_x: 1
                        radius: [30, 30, 30, 30]
                        md_bg_color: 0.98, 1, 0.98, 1
                        line_color_normal: 0, 0, 0, 0
                        line_color_focus: 0, 0, 0, 0
                        text_color_normal: 0, 0, 0, 1
                        text_color_focus: 0, 0, 0, 1

                        canvas.after:
                            Color:
                                rgba: 0, 0.8, 0, 1
                            Line:
                                width: 2.5
                                rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(4)

                    MDLabel:
                        text: "Gender: "
                        font_style: "Title"
                        role: "small"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(5)

                    BoxLayout:
                        id: gender_box
                        orientation: "horizontal"
                        spacing: "5dp"
                        size_hint_y: None
                        height: "65dp"

                        # FEMALE BUTTON
                        MDButton:
                            id: female_btn
                            style: "filled"
                            theme_bg_color: "Custom"
                            radius: [30, 30, 30, 30]
                            md_bg_color: 0.40, 0.84, 0.40, 1   # default gray
                            on_release:
                                male_btn.md_bg_color = 0.40, 0.84, 0.40, 1  # unselect other
                                self.md_bg_color = 0, 0.7, 0, 1          # selected green
                                root.selected_gender = "Female"

                            MDButtonIcon:
                                icon: "gender-female"
                                theme_icon_color: "Custom"
                                icon_color: 1, 1, 1, 1

                            MDButtonText:
                                text: "Female"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1

                        # MALE BUTTON
                        MDButton:
                            id: male_btn
                            style: "filled"
                            theme_bg_color: "Custom"
                            radius: [30, 30, 30, 30]
                            md_bg_color: 0.40, 0.84, 0.40, 1   # default
                            on_release:
                                female_btn.md_bg_color = 0.40, 0.84, 0.40, 1  # unselect other
                                self.md_bg_color = 0, 0.7, 0, 1            # selected green
                                root.selected_gender = "Male"

                            MDButtonIcon:
                                icon: "gender-male"
                                theme_icon_color: "Custom"
                                icon_color: 1, 1, 1, 1

                            MDButtonText:
                                text: "Male"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(90)
                spacing: dp(10)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(4)

                    MDLabel:
                        text: "Weight: "
                        font_style: "Title"
                        role: "small"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(5)

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(4)
                        size_hint_y: None
                        height: dp(56)

                        MDTextField:
                            id: weight_field
                            mode: "outlined"
                            size_hint_x: 1
                            radius: [30, 30, 30, 30]
                            md_bg_color: 0.98, 1, 0.98, 1
                            line_color_normal: 0, 0, 0, 0
                            line_color_focus: 0, 0, 0, 0
                            text_color_normal: 0, 0, 0, 1
                            text_color_focus: 0, 0, 0, 1

                            canvas.after:
                                Color:
                                    rgba: 0, 0.8, 0, 1
                                Line:
                                    width: 2.5
                                    rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                        MDLabel:
                            text: "kg"
                            font_style: "Title"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            size_hint_x: None
                            width: dp(30)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(4)

                    MDLabel:
                        text: "Height: "
                        font_style: "Title"
                        role: "small"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(5)

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(4)
                        size_hint_y: None
                        height: dp(56)

                        MDTextField:
                            id: height_field
                            mode: "outlined"
                            size_hint_x: 1
                            radius: [30, 30, 30, 30]
                            md_bg_color: 0.98, 1, 0.98, 1
                            line_color_normal: 0, 0, 0, 0
                            line_color_focus: 0, 0, 0, 0
                            text_color_normal: 0, 0, 0, 1
                            text_color_focus: 0, 0, 0, 1

                            canvas.after:
                                Color:
                                    rgba: 0, 0.8, 0, 1
                                Line:
                                    width: 2.5
                                    rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                        MDLabel:
                            text: "cm"
                            font_style: "Title"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            size_hint_x: None
                            width: dp(30)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "text"
                    theme_text_color: "Custom"
                    text_color: 0, 0.6, 0, 1
                    halign: "center"
                    valign: "middle"
                    text_size: self.size
                    on_release:
                        root.manager.transition.direction = "fade"
                        app.root.current = "login_screen"

                    MDButtonText:
                        text: "Already have an account?"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.validate_and_continue()

                    MDButtonText:
                        text: "Continue"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen>:', '<signupScreen2>', NEW_SIGNUP_SCREEN)

# =============================================================================
# 4. signupScreen2
# =============================================================================
NEW_SIGNUP2 = '''\
<signupScreen2>
    name: "signup_screen2"
    id: signup_screen2
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "What is your activity level?"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(12)
                size_hint_x: 0.9
                size_hint_y: None
                height: self.minimum_height
                pos_hint: {"center_x": 0.5}

                # ACTIVE BUTTON
                MDButton:
                    id: active_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        active_btn.md_bg_color = 0, 0.7, 0, 1
                        not_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        lightly_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        very_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_activitylevel = "Active"

                    MDButtonText:
                        text: "         Active          "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # NOT VERY ACTIVE BUTTON
                MDButton:
                    id: not_active_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        not_active_btn.md_bg_color = 0, 0.7, 0, 1
                        lightly_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        very_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_activitylevel = "Not Very Active"

                    MDButtonText:
                        text: " Not Very Active "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # LIGHTLY ACTIVE BUTTON
                MDButton:
                    id: lightly_active_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        not_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        lightly_active_btn.md_bg_color = 0, 0.7, 0, 1
                        very_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_activitylevel = "Lightly Active"

                    MDButtonText:
                        text: "   Lightly Active   "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # VERY ACTIVE BUTTON
                MDButton:
                    id: very_active_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        not_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        lightly_active_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        very_active_btn.md_bg_color = 0, 0.7, 0, 1
                        root.selected_activitylevel = "Very Active"

                    MDButtonText:
                        text: "     Very Active     "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "tonal"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.manager.transition.direction = "fade"
                        app.root.current = "signup_screen"

                    MDButtonText:
                        text: "Back"
                        font_style: "Title"
                        role: "large"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.validate_and_continue()

                    MDButtonText:
                        text: "Continue"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen2>', '<signupScreen3>', NEW_SIGNUP2)

# =============================================================================
# 5. signupScreen3
# =============================================================================
NEW_SIGNUP3 = '''\
<signupScreen3>
    name: "signup_screen3"
    id: signup_screen3
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "What is your goal?"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(8)
                size_hint_x: 0.9
                size_hint_y: None
                height: self.minimum_height
                pos_hint: {"center_x": 0.5}

                # Lose weight BUTTON
                MDButton:
                    id: loss_weight_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        loss_weight_btn.md_bg_color = 0, 0.7, 0, 1
                        gain_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        keep_fit_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_muscles_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_goal = "Lose weight"

                    MDButtonText:
                        text: "     Lose weight     "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # Gain weight BUTTON
                MDButton:
                    id: gain_weight_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        loss_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_weight_btn.md_bg_color = 0, 0.7, 0, 1
                        keep_fit_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_muscles_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_goal = "Gain weight"

                    MDButtonText:
                        text: "     Gain weight      "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # Keep fit BUTTON
                MDButton:
                    id: keep_fit_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        loss_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        keep_fit_btn.md_bg_color = 0, 0.7, 0, 1
                        gain_muscles_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_goal = "Keep fit"

                    MDButtonText:
                        text: "         Keep Fit         "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # Gain muscles BUTTON
                MDButton:
                    id: gain_muscles_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        loss_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_weight_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        keep_fit_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        gain_muscles_btn.md_bg_color = 0, 0.7, 0, 1
                        root.selected_goal = "Gain muscles "

                    MDButtonText:
                        text: "    Gain muscles    "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(80)
                spacing: dp(10)

                MDLabel:
                    text: "Desired Weight: "
                    font_style: "Title"
                    role: "small"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    size_hint_x: None
                    width: dp(120)
                    pos_hint: {"center_y": 0.5}

                MDTextField:
                    id: desired_weight_input
                    mode: "outlined"
                    size_hint_x: 1
                    radius: [30, 30, 30, 30]
                    md_bg_color: 0.98, 1, 0.98, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0, 0, 0, 0
                    text_color_normal: 0, 0, 0, 1
                    text_color_focus: 0, 0, 0, 1

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1          # green border
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDLabel:
                    text: "kg"
                    font_style: "Title"
                    role: "small"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    size_hint_x: None
                    width: dp(30)
                    pos_hint: {"center_y": 0.5}

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "tonal"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.manager.transition.direction = "fade"
                        app.root.current = "signup_screen2"

                    MDButtonText:
                        text: "Back"
                        font_style: "Title"
                        role: "large"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.validate_and_continue()

                    MDButtonText:
                        text: "Continue"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen3>', '<signupScreen4>', NEW_SIGNUP3)

# =============================================================================
# 6. signupScreen4
# =============================================================================
NEW_SIGNUP4 = '''\
<signupScreen4>
    name: "signup_screen4"
    id: signup_screen4
    selected_healthconditions: []
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "Do you have any health conditions?"
                font_style: "Title"
                role: "large"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(15)
                size_hint_x: 0.9
                size_hint_y: None
                height: "60dp"
                pos_hint: {"center_x": 0.5}

                # Yes BUTTON
                MDButton:
                    id: yes_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        yes_btn.md_bg_color = 0, 0.7, 0, 1
                        no_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        root.selected_boolean_healthcondition = "Yes"

                    MDButtonText:
                        text: " Yes "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

                # No BUTTON
                MDButton:
                    id: no_btn
                    style: "filled"
                    theme_bg_color: "Custom"
                    radius: [30, 30, 30, 30]
                    theme_width: "Custom"
                    size_hint_x: 1
                    height: "60dp"
                    md_bg_color: 0.40, 0.84, 0.40, 1   # default
                    on_release:
                        yes_btn.md_bg_color = 0.40, 0.84, 0.40, 1   # default
                        no_btn.md_bg_color = 0, 0.7, 0, 1
                        root.selected_boolean_healthcondition = "No"
                        root.selected_healthconditions.clear()
                        root.show_other_field = False

                    MDButtonText:
                        text: "  No  "
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Headline"
                        role: "small"

            MDBoxLayout:
                orientation: "vertical"
                spacing: "12dp"
                size_hint_y: None
                height: self.minimum_height
                opacity: 1 if root.selected_boolean_healthcondition == "Yes" else 0
                disabled: False if root.selected_boolean_healthcondition == "Yes" else True

                MDLabel:
                    text: "What health condition do you have?"
                    font_style: "Title"
                    role: "large"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(12)
                    size_hint_x: 0.9
                    size_hint_y: None
                    height: self.minimum_height
                    pos_hint: {"center_x": 0.5}

                    # Heart Disease BUTTON
                    MDButton:
                        id: heart_disease_btn
                        style: "filled"
                        theme_bg_color: "Custom"
                        radius: [30, 30, 30, 30]
                        theme_width: "Custom"
                        size_hint_x: 1
                        height: "60dp"
                        md_bg_color: 0.40, 0.84, 0.40, 1   # default
                        on_release:
                            root.toggle_condition("heart_disease", heart_disease_btn)

                        MDButtonText:
                            text: "     Heart Disease     "
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Headline"
                            role: "small"

                    # Asthma BUTTON
                    MDButton:
                        id: asthma_btn
                        style: "filled"
                        theme_bg_color: "Custom"
                        radius: [30, 30, 30, 30]
                        theme_width: "Custom"
                        size_hint_x: 1
                        height: "60dp"
                        md_bg_color: 0.40, 0.84, 0.40, 1   # default
                        on_release:
                            root.toggle_condition("Asthma", asthma_btn)

                        MDButtonText:
                            text: "          Asthma           "
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Headline"
                            role: "small"

                    # Others BUTTON
                    MDButton:
                        id: others_btn
                        style: "filled"
                        theme_bg_color: "Custom"
                        radius: [30, 30, 30, 30]
                        theme_width: "Custom"
                        size_hint_x: 1
                        height: "60dp"
                        md_bg_color: 0.40, 0.84, 0.40, 1   # default
                        on_release:
                            root.toggle_condition("Others", others_btn)

                        MDButtonText:
                            text: "           Others            "
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "Headline"
                            role: "small"

                    # TEXTFIELD FOR "OTHER CONDITION"
                    MDTextField:
                        id: other_condition_input
                        hint_text: "Please specify your condition"
                        mode: "outlined"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                        radius: [30, 30, 30, 30]
                        opacity: 1 if root.show_other_field else 0
                        disabled: False if root.show_other_field else True
                        md_bg_color: 0.98, 1, 0.98, 1
                        line_color_normal: 0, 0, 0, 0
                        line_color_focus: 0, 0, 0, 0
                        text_color_normal: 0, 0, 0, 1
                        text_color_focus: 0, 0, 0, 1

                        canvas.after:
                            Color:
                                rgba: 0, 0.8, 0, 1   # Green border
                            Line:
                                width: 2.5
                                rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "tonal"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.manager.transition.direction = "fade"
                        app.root.current = "signup_screen3"

                    MDButtonText:
                        text: "Back"
                        font_style: "Title"
                        role: "large"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.validate_and_continue()

                    MDButtonText:
                        text: "Continue"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen4>', '<signupScreen5>', NEW_SIGNUP4)

# =============================================================================
# 7. signupScreen5
# =============================================================================
NEW_SIGNUP5 = '''\
<signupScreen5>
    name: "signup_screen5"
    id: signup_screen5
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "Create Your Profile"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDLabel:
                text: "Username: "
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDTextField:
                id: username_field
                mode: "outlined"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                radius: [30, 30, 30, 30]
                md_bg_color: 0.98, 1, 0.98, 1
                line_color_normal: 0, 0, 0, 0
                line_color_focus: 0, 0, 0, 0
                text_color_normal: 0, 0, 0, 1
                text_color_focus: 0, 0, 0, 1

                canvas.after:
                    Color:
                        rgba: 0, 0.8, 0, 1
                    Line:
                        width: 2.5
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDTextFieldTrailingIcon:
                    icon: "account"
                    theme_icon_color: "Custom"
                    icon_color_normal: 0, 0.8, 0, 1   # green when unfocused
                    icon_color_focus: 0, 0.8, 0, 1

            MDLabel:
                text: "Email: "
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDTextField:
                id: email_field
                mode: "outlined"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                radius: [30, 30, 30, 30]
                md_bg_color: 0.98, 1, 0.98, 1
                line_color_normal: 0, 0, 0, 0
                line_color_focus: 0, 0, 0, 0
                text_color_normal: 0, 0, 0, 1
                text_color_focus: 0, 0, 0, 1

                canvas.after:
                    Color:
                        rgba: 0, 0.8, 0, 1
                    Line:
                        width: 2.5
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDTextFieldTrailingIcon:
                    icon: "email"
                    theme_icon_color: "Custom"
                    icon_color_normal: 0, 0.8, 0, 1   # green when unfocused
                    icon_color_focus: 0, 0.8, 0, 1

            MDLabel:
                text: "Password: "
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(56)
                spacing: dp(4)

                MDTextField:
                    id: password_field
                    mode: "outlined"
                    size_hint_x: 1
                    password: True
                    password_mask: "\\u2022"
                    radius: [30, 30, 30, 30]
                    md_bg_color: 0.98, 1, 0.98, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0, 0, 0, 0
                    text_color_normal: 0, 0, 0, 1
                    text_color_focus: 0, 0, 0, 1

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDIconButton:
                    id: password_eye_icon
                    icon: "eye-off"
                    size_hint: None, None
                    size: "32dp", "32dp"
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0.639, 0, 1
                    on_release:
                        root.toggle_password_visibility(password_field, self)

            MDLabel:
                text: "Confirm Password: "
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(56)
                spacing: dp(4)

                MDTextField:
                    id: con_password_field
                    mode: "outlined"
                    size_hint_x: 1
                    password: True
                    password_mask: "\\u2022"
                    radius: [30, 30, 30, 30]
                    md_bg_color: 0.98, 1, 0.98, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0, 0, 0, 0
                    text_color_normal: 0, 0, 0, 1
                    text_color_focus: 0, 0, 0, 1

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDIconButton:
                    id: confirm_password_eye_icon
                    icon: "eye-off"
                    size_hint: None, None
                    size: "32dp", "32dp"
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0.639, 0, 1
                    on_release:
                        root.toggle_password_visibility(con_password_field, self)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "tonal"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.manager.transition.direction = "fade"
                        app.root.current = "signup_screen4"

                    MDButtonText:
                        text: "Back"
                        font_style: "Title"
                        role: "large"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.validate_and_create_account()

                    MDButtonText:
                        text: "Sign Up"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen5>', '<signupScreen6>', NEW_SIGNUP5)

# =============================================================================
# 8. signupScreen6
# =============================================================================
NEW_SIGNUP6 = '''\
<signupScreen6>
    name: "signup_screen6"
    id: signup_screen6
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "Add Profile Photo"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            Image:
                id: profile_img
                source: "profile_default.png"
                size_hint: None, None
                width: "200dp"
                height: "200dp"
                pos_hint: {"center_x": 0.5}

            MDIconButton:
                icon: "plus"
                style: "filled"
                halign: "center"
                pos_hint: {"center_x": 0.5}
                on_release:
                    root.manager.transition.direction = "fade"
                    root.open_file_manager()

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "60dp"
                spacing: dp(20)
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}

                MDButton:
                    style: "tonal"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.manager.transition.direction = "fade"
                        root.skip_photo()

                    MDButtonText:
                        text: "Not now"
                        font_style: "Title"
                        role: "large"

                MDButton:
                    style: "filled"
                    halign: "center"
                    radius: [20, 20, 20, 20]
                    on_release:
                        root.save_profile_photo()

                    MDButtonText:
                        text: "Continue"
                        font_style: "Title"
                        role: "large"

'''

content = replace_block(content, '<signupScreen6>', '<SignupScreen7>', NEW_SIGNUP6)

# =============================================================================
# 9. SignupScreen7
# =============================================================================
NEW_SIGNUP7 = '''\
<SignupScreen7>
    name: "signup_screen7"
    id: signup_screen7
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(70)
                spacing: dp(10)

                Image:
                    source: "logo.png"
                    size_hint: None, None
                    width: "60dp"
                    height: "60dp"
                    pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Fitness Go"
                    font_style: "Headline"
                    role: "medium"
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "Congratulations!"
                font_style: "Headline"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDLabel:
                text: "You have successfully created an account"
                font_style: "Title"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                text: "Your daily net goal is"
                font_style: "Title"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                id: dailycaloriegoal_message
                text: ""
                font_style: "Headline"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                text: "Your current BMI is"
                font_style: "Title"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                id: bmi_message
                text: ""
                font_style: "Headline"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                id: bmi_status
                text: ""
                font_style: "Title"
                halign: "center"
                italic: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDLabel:
                text: "Trust the Process!"
                font_style: "Headline"
                role: "large"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDButton:
                style: "filled"
                halign: "center"
                pos_hint: {"center_x": .75}
                radius: [20, 20, 20, 20]
                on_release:
                    root.go_to_dashboard()

                MDButtonText:
                    text: "Continue"
                    font_style: "Title"
                    role: "large"

'''

content = replace_block(content, '<SignupScreen7>', '<dashboardScreen>:', NEW_SIGNUP7)

# =============================================================================
# 10. CalorieCounterScreen
# =============================================================================
NEW_CALORIE_SCREEN = '''\
<CalorieCounterScreen>
    name: "calorie_counter_screen"
    id: calorie_counter_screen
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDBoxLayout:
        orientation: "vertical"

        MDScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)

                    Image:
                        source: "logo.png"
                        size_hint: None, None
                        width: "50dp"
                        height: "50dp"
                        pos_hint: {"center_y": 0.5}

                    MDLabel:
                        text: "Calorie Counter"
                        font_style: "Headline"
                        role: "small"
                        halign: "left"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        bold: True
                        pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Keep track of your food intake"
                    font_style: "Headline"
                    role: "small"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    size_hint_y: None
                    height: self.texture_size[1] + dp(5)

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    size_hint_y: None
                    height: dp(70)
                    spacing: dp(10)

                    MDBoxLayout:
                        orientation: "vertical"
                        md_bg_color: ((0.172, 0.686, 0.161, 1))
                        padding: 10
                        spacing: 10
                        radius: [30, 30, 30, 30]
                        elevation: 0

                        MDLabel:
                            id: calorie_intake
                            halign: "center"
                            text: "Calorie Intake\\n0  "
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1

                    MDBoxLayout:
                        orientation: "vertical"
                        md_bg_color: ((0.172, 0.686, 0.161, 1))
                        padding: 10
                        spacing: 10
                        radius: [30, 30, 30, 30]
                        elevation: 0

                        MDLabel:
                            id: calorie_left
                            halign: "center"
                            text: "Calorie Left\\n0  "
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1

                MDLabel:
                    text: "Food Type: "
                    font_style: "Title"
                    role: "medium"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    size_hint_y: None
                    height: self.texture_size[1] + dp(5)

                MDTextField:
                    id: foodtype
                    mode: "outlined"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    bold: True
                    radius: [30, 30, 30, 30]

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1      # green border
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                    MDTextFieldTrailingIcon:
                        icon: "food"
                        theme_icon_color: "Custom"
                        icon_color_normal: 0, 0.8, 0, 1
                        icon_color_focus: 0, 0.8, 0, 1

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    size_hint_y: None
                    height: dp(90)
                    spacing: dp(10)

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(4)

                        MDLabel:
                            text: "Food Quantity(g): "
                            font_style: "Title"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            size_hint_y: None
                            height: self.texture_size[1] + dp(5)

                        MDTextField:
                            id: foodweight
                            mode: "outlined"
                            size_hint_x: 1
                            bold: True
                            radius: [30, 30, 30, 30]

                            canvas.after:
                                Color:
                                    rgba: 0, 0.8, 0, 1      # green border
                                Line:
                                    width: 2.5
                                    rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                            MDTextFieldTrailingIcon:
                                icon: "scale"
                                theme_icon_color: "Custom"
                                icon_color_normal: 0, 0.8, 0, 1
                                icon_color_focus: 0, 0.8, 0, 1

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(4)

                        MDLabel:
                            text: "Select Meal:"
                            font_style: "Title"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            size_hint_y: None
                            height: self.texture_size[1] + dp(5)

                        MDTextField:
                            id: selectmeal
                            mode: "outlined"
                            size_hint_x: 1
                            bold: True
                            readonly: True
                            radius: [30, 30, 30, 30]
                            on_focus:
                                if self.focus: root.open_meal_dropdown(self)

                            canvas.after:
                                Color:
                                    rgba: 0, 0.8, 0, 1      # green border
                                Line:
                                    width: 2.5
                                    rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                            MDTextFieldTrailingIcon:
                                icon: "menu-down"
                                theme_icon_color: "Custom"
                                icon_color_normal: 0, 0.8, 0, 1
                                icon_color_focus: 0, 0.8, 0, 1

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    size_hint_y: None
                    height: dp(90)
                    spacing: dp(10)

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(4)

                        # FOOD CALORIE (API result)
                        MDLabel:
                            text: "Food Calorie:"
                            font_style: "Title"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            size_hint_y: None
                            height: self.texture_size[1] + dp(5)

                        MDTextField:
                            id: foodcalorie
                            text: ""
                            mode: "outlined"
                            size_hint_x: 1
                            bold: True
                            radius: [30, 30, 30, 30]
                            readonly: True         # prevents typing
                            focus: False           # no focus/highlight
                            disabled: True

                            canvas.after:
                                Color:
                                    rgba: 0, 0.8, 0, 1      # green border
                                Line:
                                    width: 2.5
                                    rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                    MDBoxLayout:
                        id: action_box
                        orientation: "vertical"
                        spacing: dp(10)
                        size_hint_x: None
                        width: dp(160)

                        # GET CALORIES BUTTON (Light Green)
                        MDButton:
                            id: get_calories_btn
                            style: "filled"
                            theme_bg_color: "Custom"
                            radius: [15, 15, 15, 15]
                            md_bg_color: 0.40, 0.84, 0.40, 1   # light green (#66ff66)
                            on_release:
                                root.get_food_calories()

                            MDButtonText:
                                text: "Get Calories"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1  # white text

                        # SAVE BUTTON (Dark Green)
                        MDButton:
                            id: save_btn
                            style: "filled"
                            theme_bg_color: "Custom"
                            radius: [15, 15, 15, 15]
                            md_bg_color: 0.0, 0.60, 0.0, 1   # darker green
                            on_release:
                                save_btn.md_bg_color = 0, 0.7, 0, 1          # selected → dark green
                                get_calories_btn.md_bg_color = 0.40, 0.84, 0.40, 1 # unselect → light green
                                root.save_food_entry()

                            MDButtonIcon:
                                icon: "content-save"
                                theme_icon_color: "Custom"
                                icon_color: 1, 1, 1, 1

                            MDButtonText:
                                text: "   Save     "
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1  # white text

        MDBoxLayout:
            size_hint_y: None
            height: "80dp"
            padding: 13
            md_bg_color: (0.902, 0.902, 0.902, 1)

            MDCard:
                size_hint: 1, None
                height: "70dp"
                radius: [30, 30, 30, 30]
                md_bg_color: 1, 1, 1, 1
                style: "outlined"
                line_color: 0, 0.6, 0, 1
                stroke_width: 2
                elevation: 0
                padding: [20, 8, 20, 8]

                MDBoxLayout:
                    spacing: 30
                    halign: "center"

                    # --- AI ---
                    BoxLayout:
                        orientation: "vertical"
                        spacing: 2
                        MDIconButton:
                            icon: "robot"
                            theme_icon_color: "Custom"
                            icon_color: 0, 0.6, 0, 1
                            on_release:
                                app.root.current = "ai_fitness_buddy_screen"

                        MDLabel:
                            text: "Fitness \\nBuddy"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0.6, 0, 1
                            theme_font_size: "Custom"
                            font_size: "10sp"

                    # --- Calorie Counter ---
                    BoxLayout:
                        orientation: "vertical"
                        spacing: 2
                        MDIconButton:
                            icon: "food"
                            theme_icon_color: "Custom"
                            icon_color: 0, 0.6, 0, 1
                            on_release:
                                root.go_to_calorie_counter()

                        MDLabel:
                            text: "Calorie Counter"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0.6, 0, 1
                            theme_font_size: "Custom"
                            font_size: "10sp"

                    MDIconButton:
                        icon: "home"
                        style: "filled"
                        theme_bg_color: "Custom"
                        md_bg_color: 0, 0.6, 0, 1
                        theme_icon_size: "Custom"
                        icon_size: "9000dp"

                        size_hint: None, None
                        size: "60dp", "60dp"
                        on_release:
                            app.root.current = "dashboard_screen"

                    # --- ACTIVITY LOG ---
                    BoxLayout:
                        orientation: "vertical"
                        spacing: 2
                        width: dp(80)

                        MDIconButton:
                            icon: "clipboard-text"
                            theme_icon_color: "Custom"
                            icon_color: 0, 0.6, 0, 1
                            on_release:
                                root.go_to_food_log()

                        MDLabel:
                            text: "Activity \\nLog"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0.6, 0, 1
                            pos_hint: {"center_x": .5}
                            theme_font_size: "Custom"
                            font_size: "10sp"
                            size_hint_x: None
                            width: dp(60)      # ← give the text proper space

                    # --- WELLNESS HUB ---
                    BoxLayout:
                        orientation: "vertical"
                        spacing: 2
                        width: dp(80)

                        MDIconButton:
                            icon: "spa"
                            theme_icon_color: "Custom"
                            icon_color: 0, 0.6, 0, 1
                            on_release:
                                root.go_to_exercise_hub()

                        MDLabel:
                            text: "Wellness Hub"
                            pos_hint: {"center_x": .5}
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0.6, 0, 1
                            theme_font_size: "Custom"
                            font_size: "10sp"
                            size_hint_x: None
                            width: dp(60)

'''

content = replace_block(content, '<CalorieCounterScreen>', '<FoodLogScreen>', NEW_CALORIE_SCREEN)

# =============================================================================
# 11. admin_loginScreen
# =============================================================================
NEW_ADMIN_LOGIN = '''\
<admin_loginScreen>:
    name: "admin_login_screen"
    id: admin_login_screen
    md_bg_color: (0.902, 0.902, 0.902, 1)

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            Image:
                source: "logo.png"
                size_hint: None, None
                width: "150dp"
                height: "150dp"
                pos_hint: {"center_x": 0.5}

            MDLabel:
                text: "Fitness Go"
                font_style: "Display"
                role: "medium"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDLabel:
                text: "Username: "
                font_style: "Title"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDTextField:
                id: username_field
                mode: "outlined"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                radius: [30, 30, 30, 30]
                md_bg_color: 0.98, 1, 0.98, 1
                line_color_normal: 0, 0, 0, 0
                line_color_focus: 0, 0, 0, 0
                text_color_normal: 0, 0, 0, 1
                text_color_focus: 0, 0, 0, 1

                # ✅ canvas.after MUST come before child widgets
                canvas.after:
                    Color:
                        rgba: 0, 0.8, 0, 1
                    Line:
                        width: 2.5
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDTextFieldTrailingIcon:
                    icon: "account"
                    theme_icon_color: "Custom"
                    icon_color_normal: 0, 0.8, 0, 1   # green when unfocused
                    icon_color_focus: 0, 0.8, 0, 1

            MDLabel:
                text: "Password: "
                font_style: "Title"
                role: "small"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1] + dp(5)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                size_hint_y: None
                height: dp(56)
                spacing: dp(4)

                MDTextField:
                    id: password_field
                    mode: "outlined"
                    size_hint_x: 1
                    password_mask: "\\u2022"
                    radius: [30, 30, 30, 30]
                    password: True
                    md_bg_color: 0.98, 1, 0.98, 1
                    line_color_normal: 0, 0, 0, 0
                    line_color_focus: 0, 0, 0, 0
                    text_color_normal: 0, 0, 0, 1
                    text_color_focus: 0, 0, 0, 1

                    canvas.after:
                        Color:
                            rgba: 0, 0.8, 0, 1
                        Line:
                            width: 2.5
                            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)

                MDIconButton:
                    id: login_eye_icon
                    icon: "eye-off"
                    size_hint: None, None
                    size: "32dp", "32dp"
                    pos_hint: {"center_y": 0.5}
                    theme_icon_color: "Custom"
                    icon_color: 0, 0.639, 0, 1
                    on_release:
                        root.toggle_password_visibility(password_field, self)

            MDButton:
                id: login_button
                style: "filled"
                pos_hint: {"center_x": 0.5}
                on_release:
                    root.manager.transition.direction = "fade"
                    root.login_admin()

                MDButtonText:
                    text: "Log In"


'''

content = replace_block(content, '<admin_loginScreen>:', '<AdminDashboardScreen>:', NEW_ADMIN_LOGIN)

# =============================================================================
# 12. ProfileScreen — fix wide buttons (size_hint_x: None + width: "480dp")
# =============================================================================
# Fix edit_profile button
content = content.replace(
    '            MDButton:\n                id: edit_profile\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: None\n                width: "480dp"\n                height: "40dp"',
    '            MDButton:\n                id: edit_profile\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: 1\n                height: "40dp"'
)

# Fix faqs_account_btn button
content = content.replace(
    '            MDButton:\n                id: faqs_account_btn\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: None\n                width: "480dp"\n                height: "40dp"',
    '            MDButton:\n                id: faqs_account_btn\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: 1\n                height: "40dp"'
)

# Fix change_pass button
content = content.replace(
    '            MDButton:\n                id: change_pass\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: None\n                width: "480dp"\n                height: "40dp"',
    '            MDButton:\n                id: change_pass\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: 1\n                height: "40dp"'
)

# Fix logout_btn — remove the duplicate size_hint_x: None line
content = content.replace(
    '            MDButton:\n                id: logout_btn\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: None\n                size_hint_x: 1\n                height: "40dp"',
    '            MDButton:\n                id: logout_btn\n                style: "filled"\n                theme_bg_color: "Custom"\n                radius: [30, 30, 30, 30]\n                size_hint_x: 1\n                height: "40dp"'
)

# =============================================================================
# Write output
# =============================================================================
with open(KV_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content)
print(f"\nDone! Original size: {original_len} chars → New size: {new_len} chars")
print(f"Line count: {content.count(chr(10))}")
