import * as React from "react"

const TOAST_LIMIT = 1
const TOAST_REMOVE_DELAY = 1000000

type ToastT = {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: React.ReactNode
  variant?: "default" | "destructive"
}

type ActionType =
  | { type: "ADD_TOAST"; toast: ToastT }
  | { type: "UPDATE_TOAST"; toast: Partial<ToastT> }
  | { type: "DISMISS_TOAST"; toastId?: string }
  | { type: "REMOVE_TOAST"; toastId?: string }

interface State {
  toasts: ToastT[]
}

const initialState: State = { toasts: [] }

function reducer(state: State, action: ActionType): State {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }

    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      }

    case "DISMISS_TOAST": {
      const toastToUpdate = state.toasts.find(
        (t) => t.id === action.toastId
      )

      if (!toastToUpdate) {
        return state
      }

      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toastId ? { ...t, variant: "destructive" } : t
        ),
      }
    }
    case "REMOVE_TOAST":
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      }
  }
}

function generateId() {
  return Math.random().toString(36).substring(2, 9)
}

export function useToast() {
  const [state, dispatch] = React.useReducer(reducer, initialState)

  const toast = React.useCallback((opts: Omit<ToastT, "id">) => {
    const id = generateId()

    const update = (props: ToastT) =>
      dispatch({
        type: "UPDATE_TOAST",
        toast: { ...props, id },
      })

    const dismiss = () => dispatch({ type: "DISMISS_TOAST", toastId: id })

    dispatch({
      type: "ADD_TOAST",
      toast: {
        ...opts,
        id,
        variant: opts.variant ?? "default",
      },
    })

    return {
      id: id,
      dismiss,
      update,
    }
  }, [])

  return {
    ...state,
    toast,
    dismiss: (toastId?: string) => dispatch({ type: "REMOVE_TOAST", toastId }),
  }
}
