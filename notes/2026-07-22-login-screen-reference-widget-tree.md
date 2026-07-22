# Login Screen — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-22 via Mentor inspection. Ground truth for Login screen layout spec.

---

- **WebBlockInstance** — `LayoutBlankInstance`
  - Style: *(empty)*
  - Block: `LayoutBlank` (from `Layouts` flow)
  - Parameters: `ExtendedClass` → *(null)*, `EnableAccessibilityFeatures` → *(default)*

  - **[Placeholder: Content]**

    - **Container** — *(auto-named)*
      - Style: `"login-screen"`
      - CustomStyle: *(empty)*
      - Visible: `True`
      - Width: `(fill parent)`

      - **Form** — `LoginForm`
        - Style: `"login-form"`
        - Width: *(empty)*

        - **Container** — *(auto-named)*
          - Style: `"login-logo"`
          - CustomStyle: `text-align: center;`
          - Visible: `True`
          - Width: `(fill parent)`

          - **Container** — *(auto-named)*
            - Style: *(empty)*
            - CustomStyle: `text-align: center;`
            - Visible: `True`
            - Width: `(fill parent)`

            - **Image** — *(auto-named)*
              - Style: *(empty)*
              - CustomStyle: `height: 100px;`
              - Image: `Logo` (Static)
              - Type: Static
              - Width: *(empty)*
              - Extended property: `alt` → `""`

          - **AdvancedHtml** — *(auto-named)*
            - Tag: `h1`
            - Extended property: `class` → `"margin-y-base"`

            - **Expression** — *(auto-named)*
              - Style: `"heading5 text-neutral-8"`
              - Value: `GetAppName()`
              - Example: `Application Title`
              - Width: *(empty)*

        - **If** — `BuiltInProvider`
          - Condition: `ShowBuiltInProvider`
          - DesignMode: ShowAll

          - **[True Branch]**

            - **Container** — *(auto-named)*
              - Style: `"login-inputs"`
              - Visible: `True`
              - Width: `(fill parent)`

              - **Container** — *(auto-named)*
                - Style: *(empty)*
                - Visible: `True`
                - Width: `(fill parent)`

                - **WebBlockInstance** — `AnimatedLabelInstance` (1st — username)
                  - Block: `AnimatedLabel` (from OutSystemsUI `Interaction` flow)
                  - Parameters: `ExtendedClass` → *(default)*

                  - **[Placeholder: Label]**

                    - **Label** — *(auto-named)*
                      - Style: *(empty)*
                      - Width: `(fill parent)`
                      - Target: `Input_UsernameVal`

                      - **Text** — *(auto-named)*
                        - Text: `"Login"`

                  - **[Placeholder: Input]**

                    - **Input** — `Input_UsernameVal`
                      - Style: `"form-control"`
                      - InputType: `Text`
                      - Variable: `UserEmail`
                      - Placeholder: *(empty)*
                      - Enabled: `ExecutingIndex = -1 and not IsBuiltInExecuting`
                      - Mandatory: `True`
                      - MaxLength: `250`
                      - Width: `(fill parent)`
                      - Extended property: `tabindex` → `1`

              - **Container** — *(auto-named)*
                - Style: `"margin-top-base"`
                - Visible: `True`
                - Width: `(fill parent)`

                - **WebBlockInstance** — `AnimatedLabelInstance2` (2nd — password)
                  - Block: `AnimatedLabel` (from OutSystemsUI `Interaction` flow)
                  - Parameters: `ExtendedClass` → *(default)*

                  - **[Placeholder: Label]**

                    - **Label** — *(auto-named)*
                      - Style: *(empty)*
                      - Width: `(fill parent)`
                      - Target: `Input_Password`

                      - **Text** — *(auto-named)*
                        - Text: `"Password"`

                  - **[Placeholder: Input]**

                    - **WebBlockInstance** — `InputWithIconInstance`
                      - Block: `InputWithIcon` (from OutSystemsUI `Interaction` flow)
                      - Parameters: `ExtendedClass` → *(default)*, `AlignIconRight` → `True`

                      - **[Placeholder: Icon]**

                        - **Link** — *(auto-named)*
                          - Style: *(empty)*
                          - Enabled: `True`
                          - Visible: `True`
                          - Width: *(empty)*
                          - OnClick: `OnTogglePasswordVisibility`

                          - **If** — `PasswordVisibile`
                            - Condition: `IsPasswordVisible`
                            - DesignMode: ShowTrueOrPreview

                            - **[True Branch]**

                              - **Icon** — *(auto-named)*
                                - Icon name: `eye-slash`
                                - Weight: `regular`
                                - Style: `"icon"`
                                - IconSize: FontSize
                                - Visible: `True`

                            - **[False Branch]**

                              - **Icon** — *(auto-named)*
                                - Icon name: `eye`
                                - Weight: `regular`
                                - Style: `"icon"`
                                - IconSize: FontSize
                                - Visible: `True`

                      - **[Placeholder: Input]**

                        - **Input** — `Input_Password`
                          - Style: `"form-control login-password"`
                          - CustomStyle: `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`
                          - InputType: `Password`
                          - Variable: `Password`
                          - Placeholder: *(empty)*
                          - Enabled: `ExecutingIndex = -1 and not IsBuiltInExecuting`
                          - Mandatory: `True`
                          - MaxLength: *(null)*
                          - Width: `(fill parent)`
                          - Extended property: `tabindex` → `2`

              - **Container** — *(auto-named)*
                - Style: `"margin-top-l"`
                - Visible: `True`
                - Width: `(fill parent)`

                - **Container** — *(auto-named)*
                  - Style: *(empty)*
                  - CustomStyle: `text-align: right;`
                  - Visible: `True`
                  - Width: `(fill parent)`

                  - **Link** — *(auto-named)*
                    - Style: *(empty)*
                    - Enabled: `True`
                    - Visible: `True`
                    - Width: *(empty)*
                    - OnClick → navigates to: `RecoverPasswordRequest`
                    - Extended properties: `tabindex` → `3`, `aria-label` → `"Forgot your password? Click here to recover it"`

                    - **Text** — *(auto-named)*
                      - Text: `"Forgot your password?"`

            - **Container** — *(auto-named)*
              - Style: `"login-button margin-top-l"`
              - Visible: `True`
              - Width: `(fill parent)`

              - **WebBlockInstance** — `ButtonLoadingInstance` (built-in login button)
                - Block: `ButtonLoading` (from OutSystemsUI `Utilities` flow)
                - Parameters: `IsLoading` → `IsBuiltInExecuting`, `ShowLabelOnLoading` → *(null)*, `ExtendedClass` → `"full-width"`

                - **[Placeholder: Button]**

                  - **Button** — *(auto-named)*
                    - Style: `"btn btn-primary"`
                    - Enabled: `ExecutingIndex = -1`
                    - Visible: `True`
                    - IsDefault (IsSubmit): `true`
                    - Width: `(fill parent)`
                    - OnClick: `LoginOnClick` (with validation: ValidateAndContinue)
                    - Extended property: `tabindex` → `4`

                    - **Container** — *(auto-named)*
                      - Style: `"osui-btn-loading__spinner-animation"`
                      - Visible: `True`
                      - Width: `(fill parent)`

                    - **Text** — *(auto-named)*
                      - Text: `"Log in"`

        - **If** — `Separator`
          - Condition: `ShowBuiltInProvider and ShowExternalProvider`
          - DesignMode: ShowAll

          - **[True Branch]**

            - **Container** — *(auto-named)*
              - Style: `"display-flex justify-content-center align-items-center"`
              - Visible: `True`
              - Width: `(fill parent)`

              - **Container** — *(auto-named)*
                - Style: `"full-width"`
                - Visible: `True`
                - Width: `(fill parent)`

                - **WebBlockInstance** — `SeparatorInstance`
                  - Block: `Separator` (from OutSystemsUI `Utilities` flow)
                  - Parameters: `Color` → *(null)*, `Space` → *(null)*, `ExtendedClass` → *(default)*, `IsVertical` → *(null)*

              - **Text** — *(auto-named)*
                - Style classes: `"position-absolute padding-x-s background-neutral-0 text-neutral-8-darker font-semi-bold"`
                - Text: `"or"`

        - **If** — `ExternalProviders`
          - Condition: `ShowExternalProvider`
          - DesignMode: ShowAll

          - **[True Branch]**

            - **List** — `ListProviders`
              - Style: `"list list-group"`
              - Source: `ExternalIdentityProviders`
              - Mode: Default
              - Tag: `div`
              - Width: `(fill parent)`
              - AnimateItems: `true`

              - **Container** — *(auto-named)*
                - Style: `"margin-bottom-s"`
                - Visible: `True`
                - Width: `(fill parent)`

                - **WebBlockInstance** — `ButtonLoadingInstance2` (external provider button)
                  - Block: `ButtonLoading` (from OutSystemsUI `Utilities` flow)
                  - Parameters: `IsLoading` → `ExecutingIndex = ExternalIdentityProviders.CurrentRowNumber`, `ShowLabelOnLoading` → `False`, `ExtendedClass` → `"full-width"`

                  - **[Placeholder: Button]**

                    - **Button** — *(auto-named)*
                      - Style: `"btn"`
                      - Enabled: `ExecutingIndex = -1 and not IsBuiltInExecuting`
                      - Visible: `True`
                      - IsDefault (IsSubmit): `false`
                      - Width: `(fill parent)`
                      - OnClick: `LoginProviderOnClick` (with validation: ValidateAndContinue)
                        - Arguments: `ProviderIndex` → `ExternalIdentityProviders.CurrentRowNumber`, `ProviderKey` → `ExternalIdentityProviders.Current.Key`
                      - Extended property: `tabindex` → `5`

                      - **Container** — *(auto-named)*
                        - Style: `"osui-btn-loading__spinner-animation"`
                        - Visible: `True`
                        - Width: `(fill parent)`

                      - **Text** — *(auto-named)*
                        - Text: `"Continue with "`

                      - **Expression** — *(auto-named)*
                        - Style: *(empty)*
                        - Value: `ExternalIdentityProviders.Current.Name`
                        - Example: `Apple`
                        - Width: *(empty)*
