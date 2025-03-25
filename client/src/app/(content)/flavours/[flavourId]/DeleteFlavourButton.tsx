"use client";

import { startTransition, useActionState, useRef } from "react";
import { Trash2 } from "lucide-react";
import classNames from "classnames";

interface DeleteFlavourButtonProps {
  onDelete: () => Promise<null>;
}

export default function DeleteFlavourButton({
  onDelete,
}: DeleteFlavourButtonProps) {
  const [, formAction, isDeleting] = useActionState(onDelete, null);

  const modalRef = useRef<HTMLDialogElement>(null);

  return (
    <>
      <button
        onClick={() => modalRef.current?.showModal()}
        className="btn btn-error text-white"
        title="Delete flavour"
      >
        <Trash2 size={16} />
        <span>Delete</span>
      </button>

      <dialog ref={modalRef} className="modal">
        <div className="modal-box">
          <h3 className="text-lg font-bold">Delete flavour?</h3>
          <p className="py-4">
            Are you sure you want to delete this flavour? This action cannot be
            undone.
          </p>
          <div className="modal-action">
            <form method="dialog">
              <button className="btn">Close</button>
            </form>
            <button
              className={classNames("btn btn-error text-white", {
                loading: isDeleting,
              })}
              onClick={async () => startTransition(() => formAction())}
            >
              Delete
            </button>
          </div>
        </div>
      </dialog>
    </>
  );
}
