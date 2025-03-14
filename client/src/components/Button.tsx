export default function Button({
  children,
  onClick,
}: {
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="cursor-pointer bg-slate-600 text-white font-medium px-4 py-2 rounded-md"
    >
      {children}
    </button>
  );
}
