import { cn } from "../../utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "ghost";
  size?: "default" | "icon";
}

export function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
        variant === "default" &&
          "bg-[#38bdf8] hover:bg-[#0ea5e9] text-white focus:ring-[#38bdf8]",
        variant === "ghost" &&
          "bg-transparent hover:bg-gray-100 text-gray-700 focus:ring-gray-200",
        size === "default" && "h-10 px-4 py-2",
        size === "icon" && "h-10 w-10",
        className
      )}
      {...props}
    />
  );
}
